# coding = utf - 8
import sys
sys.path.append("../../")

import os
import json
import re
import time,datetime
from collections import defaultdict
from textrank4zh import TextRank4Keyword, TextRank4Sentence
from Cron.profile_cal.data_process_utils import wordcount
from Cron.profile_cal.data_utils import sql_insert_many
from Config.db_utils import es, pi_cur, conn

cursor = pi_cur()

#从敏感词列表中读取敏感词及其程度 得到{词：敏感程度}
def sensitive_word():
    sensitive_words_weight={}
    for b in open('../profile_cal/sensitive_words.txt', 'r'):
        word = b.strip().split('\t')[0]
        weight =  b.strip().split('\t')[1]
        sensitive_words_weight[word] = weight
    return sensitive_words_weight


#输入为训练字典已有文件中读出的权重字典和测试字典{uid:{词：词频} 
def get_p(train_dict,test_dict):
    
    p_dict=defaultdict(dict)
    train_word = set(train_dict.keys())
    for k,v in test_dict.items():
        result_p={}
        test_word = set(v.keys())
        #for i,j in train_dict.items():
            #train_word = set(j.keys())
        c_set = test_word & train_word
            #print(c_set)
        for n in c_set:
            p=0
            p = float(train_dict[n]*v[n]) 
            result_p[n]=p
        result_p = dict(sorted(result_p.items(),key = lambda x:x[1], reverse = True))
        p_dict[k]=result_p
    return p_dict


#计算用户关键词、话题、敏感词并保存
#输入text_list为{uid:[text]}未分词,word_dict为分词后的词频字典；
#输出为关键词字典列表{uid:{keyword:count}}和话题字典列表{uid:{hastag:count}}和敏感词字典{uid:{敏感词：比重}}
def get_user_keywords(text_list,word_dict,date, keywords_num=5):
    keywords = []
    hastag_dict=defaultdict(list)
    hastag = {}
    user_kw={}
    keywords_dict=defaultdict(dict)
    text_all=""
    #thedate = datetime.date.today()
    tr4w = TextRank4Keyword()
    #time11 = time.time()
    td = date + " 00:00:00"
    ta = time.strptime(td, "%Y-%m-%d %H:%M:%S")
    ts = int(time.mktime(ta))
    for k,v in text_list.items():
        for text in v:
            if isinstance(text, str):
                RE = re.compile(r'#([a-zA-Z-_⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]+)#', re.UNICODE)
                #print(RE.findall(text))
                #RE = re.compile(u"#.[\u4e00-\u9fa5]+#")
                #print(text)
                ht = RE.findall(text.encode('utf-8').decode('utf-8'))
                if len(ht):
                    for h in ht:
                        if h in hastag:
                            hastag[h] += 1
                        else:
                            hastag[h] = 1
                tr4w.analyze(text=text, lower=True, window=2)   # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象
                for item in tr4w.get_keywords(keywords_num, word_min_len= 1):
                    #print(item.word,item.weight)
                    try:
                        keywords_dict[k][item['word']] += item['weight']
                    except:
                        keywords_dict[k][item['word']] = item['weight']
                #print(json.dumps(keywords_dict[k],ensure_ascii=False))
        hastag_dict[k] = hastag
        #print(hastag)
        #keywords_dict[k] = keywords
    #print(hastag_dict)
    #time22 = time.time()
    #print("获取关键词和has花费：",time22-time11)
    #time2 = time.time()
    #print("wordcount花费：",time2-time22)
    sensitive_words_weight = sensitive_word()
    #time3=time.time()
    #print("读取敏感词花费：",time3-time2)
    stw_dict = get_p(sensitive_words_weight,word_dict)
    #time4 = time.time()
    #print("获取概率：",time4-time3)
    for k in word_dict:
        #if len(keywords_dict):
        keyword_json = json.dumps(keywords_dict[k],ensure_ascii=False)
        #print(keyword_json)
        #if len(hastag_dict):
        hastag_json = json.dumps(hastag_dict[k],ensure_ascii=False)
        #if len(stw_dict):
        stw_json = json.dumps(stw_dict[k],ensure_ascii=False)
        user_kw["%s_%s" % (str(ts), k)]={"uid": k,
                                                        "timestamp": ts,
                                                        "keywords":keyword_json,
                                                        "hastags":hastag_json,
                                                        "sensitive_words":stw_json,
                                                        "store_date":date}
    sql_insert_many(cursor, "UserKeyWord", "ukw_id", user_kw)
    #time5 = time.time()
    # print("插入kw花费：",time5-time4)
    #return keywords_dict,hastag_dict'''