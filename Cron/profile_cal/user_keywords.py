# coding = utf - 8
import sys
import os
import json
from collections import defaultdict
from textrank4zh import TextRank4Keyword, TextRank4Sentence
from data_process_utilis import wordcount
from data_get_utils import sql_insert_many
from Config.db_utils import es, pi_cur, conn

cursor = pi_cur()

#从敏感词列表中读取敏感词及其程度 得到{词：敏感程度}
def sensitive_word():
    for b in open(os.path.join(ABS_PATH, 'sensitive_words.txt'), 'r'):
        word = b.strip().split('\t')[0]
        weight =  b.strip().split('\t')[1]
        sensitive_words_weight[word] =  weight
    return sensitive_words_weight


#输入为训练字典已有文件中读出的权重字典和测试字典{uid:{词：词频} 
def get_p(train_dict,test_dict):
    result_p={}
    p_dict=defaultdict(list)
    for k,v in test_dict.items():
        test_word = set(v.keys())
        for i,j in train_dict.items():
            train_word = set(j.keys())
            c_set = test_word & train_word
            #print(c_set)
            p=0
            p = sum([float(j[n][0]*v[n]) for n in c_set])
            result_p[i]=p
        result_p = dict(sorted(result_p.items(),key = lambda x:x[1], reverse = True))
        p_dict[k]=result_p
    return p_dict


#计算用户关键词、话题、敏感词并保存
#输入text_list为{uid:[text]}未分词,word_dict为分词后的词频字典；
#输出为关键词字典列表{uid:{keyword:count}}和话题字典列表{uid:{hastag:count}}和敏感词字典{uid:{敏感词：比重}}
def get_user_keywords(text_list,word_dict, keywords_num=5):
    keywords = []
    hastag_dict=defaultdict(list)
    hastag = []
    keywords_dict=defaultdict(list)
    text_all=""
    tr4w = TextRank4Keyword()
    for k,v in text_list.items():
        if isinstance(v, str):
            RE = re.compile(u'#([a-zA-Z-_⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]+)#', re.UNICODE)
        # hashtag = '&'.join(RE.findall(text))
            hastag = RE.findall(v)
                #text_all += text
        hastag_dict[k] = hastag
        tr4w.analyze(text=v.encode('utf-8', 'ignore'), lower=True, window=2)   # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象
        for item in tr4w.get_keywords(keywords_num, word_min_len= 1):
            keywords.append(item.word)
        keywords_dict[k] = keywords
    hastag_dict = wordcount(hastag_dict)
    keywords_dict=wordcount(keywords_dict)
    sensitive_words_weight = sensitive_word()
    stw_dict = get_p(sensitive_words_weight,word_dict)
    for k in word_dict.keys():
        keyword_json = json.dumps(keywords_dict[k])
        hastag_json = json.dumps(hastag_dict[k])
        stw_json = json.dumps(stw_dict[k])
        user_kw["%s_%s" % (str(int(time.time())), k)]={"uid": k,
                                                        "timestamp": int(time.time()),
                                                        "keywords":keyword_json,
                                                        "hastags":hastag_json,
                                                        "sensitive_words":stw_json}
    sql_insert_many(cursor, "UserKeyword", "ukw_id", user_kw)
    #return keywords_dict,hastag_dict