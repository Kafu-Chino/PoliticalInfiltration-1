#-*-coding=utf-8-*-
import sys
import os
import json
import time
import datetime
import numpy as np
from collections import defaultdict
import pandas as pd
from data_get_utils import sql_insert_many
from Config.db_utils import es, pi_cur, conn

cursor = pi_cur()

DOMAIN_LIST=['abroadadmin','abroadmedia','business','folkorg','grassroot','activer',\
              'homeadmin','homemedia','lawyer','mediaworker','politician','university']


#得到领域的代表词及其权重tfidf
def domain_tfidf():
    ca_dict=defaultdict(dict) # {词：{domain:tfidf,....}}
    for i in DOMAIN_LIST: 
        reader = pd.read_csv('domain_dict/%s.csv' % i,header=None,names=['tfidf','word'],encoding= 'utf8')
        count = reader['tfidf'].sum()
        #print(reader)
        for row in reader.itertuples():
            ca_dict[getattr(row,'word')][i]=getattr(row,'tfidf')/count
    return ca_dict



#输入为训练字典已有文件中读出的权重字典和测试字典{uid:{词：词频} 
def get_p(train_dict,test_dict):
    
    p_dict=defaultdict(dict)
    #print(train_df)
    train_word = set(train_dict.keys())
    for k,v in test_dict.items():
        result_p={}
        train_new = defaultdict(dict)
        test_word = set(v.keys())
        c_set = test_word & train_word
        #print(c_set)
        #print(len(c_set))
        #train_df = pd.DataFrame.from_dict([train_dict[n] for n in c_set])
        test_new = np.zeros(len(c_set))
        i = 0
        for n in c_set:
            train_new[n] = train_dict[n]
            test_new[i] = v[n]/v["count"]
            i = i+1
        df = pd.DataFrame(train_new.values()).fillna(0)
        df_m = np.dot(test_new,df.values)
        #print(df_m)
        j=0
        for i in df.columns:
            result_p[i] = df_m[j]
            j=j+1
        p_dict[k] = sorted(result_p.items(),key = lambda x:x[1], reverse = True)
        #print(p_dict[k])
    return p_dict



def get_user_domain(word_dict,date):
    time1 = time.time()
    domain_dict = domain_tfidf()
    time2 = time.time()
    print("获取domain",time2-time1)
    user_domain={}
    thedate = datetime.date.today()
    domain_p = get_p(domain_dict,word_dict)
    time3 = time.time()
    print("获取概率",time3-time2)
    for k in word_dict.keys():
        domain_json = json.dumps(domain_p[k])
        if len(domain_p[k]):
            md = domain_p[k][0][0]
            #print(md)
        else:
            md = "other"
        user_domain["%s_%s" % (str(int(time.time())), k)]={"uid": k,
                                                           "timestamp": int(time.time()),
                                                           "main_domain":md,
                                                           "domains":domain_json,
                                                           "store_date":date}
    sql_insert_many(cursor, "UserDomain", "ud_id", user_domain)