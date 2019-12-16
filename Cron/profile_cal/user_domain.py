#-*-coding=utf-8-*-
import sys
import os
import json
import time
import datetime
from collections import defaultdict
import pandas as pd
from data_get_utils import sql_insert_many
from Config.db_utils import es, pi_cur, conn

cursor = pi_cur()

DOMAIN_LIST=['abroadadmin','abroadmedia','business','folkorg','grassroot','activer',\
                'homeadmin','homemedia','lawyer','mediaworker','politician','university']


#得到领域的代表词及其权重tfidf
def domain_tfidf():
    ca_dict={} #存储一类的tfidf {词：tfidf}
    domain_dict={} #话题字典{话题：{词：tfidf}}
    for i in DOMAIN_LIST: 
        reader = pd.read_csv('domain_dict/%s.csv' % i,header=None,names=['tfidf','word'],encoding= 'utf8')
        ca_dict = reader.groupby('word')['tfidf'].apply(list).to_dict()
        domain_dict[i]=ca_dict
    return domain_dict



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



def get_user_domain(word_dict):
    doamin_dict = domain_tfidf()
    user_domain={}
    domain_p = get_p(domain_dict,word_dict)
    for k in word_dict.keys():
        domain_json = json.dumps(domain_p[k])
        user_domain["%s_%s" % (str(int(time.time())), k)]={"uid": k,
                                                           "timestamp": int(time.time()),
                                                           "domains":domain_json}
    sql_insert_many(cursor, "UserDomain", "ud_id", user_domain)