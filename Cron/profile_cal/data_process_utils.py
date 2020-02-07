import re
import emoji
from pandas import DataFrame
from collections import defaultdict
import jieba
from get_user_profile import get_data_dict,sql_insert_many
import time
#from data_get_utils import sql_select_many
from Config.db_utils import es, pi_cur, conn
import datetime
import json
cursor = pi_cur()



def get_field(data_dict,field_name):
    field_dict = defaultdict(list)
    for k,v in data_dict.items():
        for item in v:
            field_dict[k].append(item[field_name])
    return field_dict


#对得到的微博文本进行去除链接、符号、空格等操作
def weibo_move(field_dict):
    if len(field_dict):
        text_dict = defaultdict(list)
        text_list = defaultdict(list)
        for k,v in field_dict.items():
            #text = ""
            for item in v:
                result = Weibo_utils()
                result.remove_c_t(item)
                item = result.remove_emoji(item)
                text = result.remove_nochn(item)
                text_list[k].append(text)
                text_dict[k].append(jieba.lcut(text,cut_all=False))
        #with open('weibocut_%s.txt' % k,"w") as f:
            #f.writelines(text_list)
        return text_list,text_dict
    else:
        print("无微博内容")



#读取停用词
def stopwordslist():
    stopwords = set([line.strip() for line in open('stop_words.txt').readlines()])
    return stopwords


#得到微博词频 
#输入为分词后的{uid:[词列表]} 返回格式为字典{uid:{词：词频}}
def wordcount(text_dict,date):
    stopwords = stopwordslist()
    #word_list = {} #统计词频后的字典{uid:词频}
    word_dict = {} #格式为字典{uid:{词：词频}}
    user_wc = {}
    for k,v in text_dict.items():
        word_list = {}
        count=0
        for item in v:
            for item1 in item:
                if item1 not in stopwords and item1 != " ":
                    count += 1
                    try:
                        word_list[item1] += 1
                    except:
                        word_list[item1] = 1 
        word_list["count"] = count
        #for w,c in word_list:
            #word_list[w] = c/count
        word_dict[k]=word_list
    thedate = datetime.date.today()
    for k in word_dict.keys():
        word_json = json.dumps(word_dict[k])
        user_wc["%s_%s" % (str(int(time.time())), k)]={"uid": k,
                                                           "timestamp": int(time.time()),
                                                           "wordcount":word_json,
                                                           "store_date":date}
    sql_insert_many(cursor, "WordCount", "uwc_id", user_wc)
    return word_dict






class Weibo_utils:
    def __init__(self):
        self.re_comment = re.compile("回复@.*?:")   # 匹配评论链
        self.re_link = re.compile('http://[a-zA-Z0-9.?/&=:]*')   # 匹配网址
        self.re_links = re.compile('https://[a-zA-Z0-9.?/&=:]*')   # 匹配网址
        try:
            self.re_emoji = re.compile(u'[\U00010000-\U0010ffff]')   # 匹配八字节emoji
        except re.error:
            self.re_emoji = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        self.re_emoji_pac = re.compile(u':.*?:')   # 匹配emoji包转换后的模式
        self.re_text = re.compile(r'[^\u4e00-\u9fa5^ ^a-z^A-Z]')   # 匹配中文空格与英文

    # 删除转发评论链
    def remove_c_t(self,text):
        text = self.re_comment.sub("", text)   # 删除转发评论链
        text = self.re_link.sub("", text)
        text = self.re_links.sub("", text)
        text = text.split("//@",1)[0]
        text = text.strip()
        if text in set(['转发微博','轉發微博','Repost','repost']):
            text = ''
        return text

    # 移除emoji
    def remove_emoji(self, text):
        text = self.re_emoji.sub("", text)
        text = emoji.demojize(text)
        text = self.re_emoji_pac.sub("", text)
        return text

    # 移除非中英文及空格
    def remove_nochn(self, text):
        text = self.re_text.sub("", text)
        return text

    def filter_weibo(self, doclist):
        doclist_new = []
        for index, text in enumerate(doclist):
            if index % 10000 == 0:
                print("dealing weibo:", index)
            text = self.remove_c_t(text)
            doclist_new.append(text)
        return doclist_new


 
def get_processed_data(data_dict,date):
    #data_dict=get_data_dict(cursor, table_name, field_name1)
    #time1 = time.time()
    field_dict = get_field(data_dict,"text")
    #time2 = time.time()
    #print("获取特定字段花费：",time2-time1)
    text_list,text_dict = weibo_move(field_dict)
    #time11 = time.time()
    #print("去除链接以及分词等花费：",time11-time2)
    word_dict = wordcount(text_dict,date)
    #time22 = time.time()
    #print("统计词频花费：",time22-time11)
    return word_dict,text_list,text_dict


if __name__ == '__main__':
    pass

