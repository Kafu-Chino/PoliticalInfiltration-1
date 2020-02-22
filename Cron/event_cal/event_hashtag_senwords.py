import re
import sys
import json
sys.path.append("../../")

from Config.db_utils import es, pi_cur, conn
from Config.time_utils import *

def event_hashtag_senwords(e_id, data, date):
    hashtag_dic = {}
    global_senwords_dic = {}
    event_senwords_dic = {}

    global_senwords_list = []
    # with open('sensitive_words_list_add.txt','r',encoding='utf-8') as f:
    #     for l in  f.readlines():
    #         global_senwords_list.append(l.strip())

    event_senwords_list = []
    # with open('高精度敏感词.txt','r',encoding='utf-8') as f:
    #     for l in  f.readlines():
    #         event_senwords_list.append(l.strip())

    re_global_senwords = re.compile('|'.join(global_senwords_list))
    re_event_senwords = re.compile('|'.join(event_senwords_list))

    re_hashtag = re.compile('#.+?#')

    for text in data:
        for hashtag in re_hashtag.findall(text):
            if hashtag in hashtag_dic:
                hashtag_dic[hashtag] += 1
            else:
                hashtag_dic[hashtag] = 1

        if global_senwords_list:
            for global_senword in re_global_senwords.findall(text):
                if global_senword in global_senwords_dic:
                    global_senwords_dic[global_senword] += 1
                else:
                    global_senwords_dic[global_senword] = 1

        if event_senwords_list:
            for event_senword in re_event_senwords.findall(text):
                if event_senword in event_senwords_dic:
                    event_senwords_dic[global_senword] += 1
                else:
                    event_senwords_dic[global_senword] = 1

    timestamp = date2ts(date)
    ehs_id = "{}_{}".format(str(timestamp), e_id)
    hashtag = json.dumps(hashtag_dic)
    global_senword = json.dumps(global_senwords_dic)
    event_senword = json.dumps(event_senwords_dic)
    sql = "REPLACE into Event_Hashtag_Senwords values(%s,%s,%s,%s,%s,%s,%s)"
    val = [(ehs_id, e_id, hashtag, global_senword, event_senword, timestamp, date)]

    cursor = pi_cur()
    n = cursor.executemany(sql, val)
    print("insert %d success" % n)
    conn.commit()