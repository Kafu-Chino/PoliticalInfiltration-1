#-*-coding=utf-8-*-
import sys
import os
import json
import time
import datetime
from collections import defaultdict
import pandas as pd
#from pandas import DataFrame 
from data_get_utils import sql_insert_many
from Config.db_utils import es, pi_cur, conn

cursor = pi_cur()

TOPIC_LIST=["art","computer","economic","education","environment","medicine",\
             "military","politics","sports","traffic","life","anti-corruption","employment",\
             "fear-of-violence","house","law","peace","religion","social-security"]


#得到话题的代表词及其权重tfidf返回{话题：{词：tfidf}}
def topic_tfidf():
    ca_dict={} #存储一类的tfidf {词：tfidf}
    topic_dict={} #话题字典{话题：{词：tfidf}}
    for i in TOPIC_LIST: 
        reader = pd.read_csv('topic_dict/%s_tfidf.csv' % i,header=None,names=['tfidf','word'],encoding= 'utf8')
        ca_dict = reader.groupby('word')['tfidf'].apply(list).to_dict() #转化为字典
        topic_dict[i]=ca_dict
    return topic_dict


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



#用户分类函数 计算用户话题和领域并保存至数据库
#输入为结巴分词后的字典{uid:词列表}
def get_user_topic(word_dict):
    topic_dict=topic_tfidf()
    thedate = datetime.date.today()
    #print(topic_dict)
    user_topic={}
    topic_p= get_p(topic_dict,word_dict)
    for k in word_dict.keys():
        topic_json = json.dumps(topic_p[k])
        user_topic["%s_%s" % (str(int(time.time())), k)]={"uid": k,
                                                          "timestamp": int(time.time()),
                                                          "topics":topic_json,
                                                          "store_date":thedate}
    sql_insert_many(cursor, "UserTopic", "ut_id", user_topic)
    #return category_dict

if __name__ == '__main__':
    topic_dict=topic_tfidf()
    topic_p= get_p(topic_dict,word_dict)