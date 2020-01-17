import math
import numpy as np
import time
import pymysql
import datetime
from elasticsearch import Elasticsearch
import json
from influence.Config import *

ES_HOST = '219.224.134.214'
ES_PORT = 9211
es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)
db = pymysql.connect(
    host='219.224.134.214',
    port=3306,
    user='root',
    passwd='mysql3306',
    db='PoliticalInfiltration',)


def search_woordcount(uid,nowtime,pretime):
    cursor = db.cursor()
    sql = "SELECT wordcount FROM  WordCount  WHERE timestamp between '%d'and '%d'and uid = '%s' limit 1" % (pretime,nowtime,uid)#timestamp between '%d'and '%d'，pretime,nowtime,
    # try:
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    return results

def get_day_activeness(user_day_activeness_geo,weibo_num, uid):
    result = 0
    # get day geo dict by ip-timestamp result

    statusnum = weibo_num
    activity_geo_count = len(user_day_activeness_geo.keys())
    result = int(activeness_weight_dict['activity_geo'] * math.log(activity_geo_count + 1) + \
                 activeness_weight_dict['statusnum'] * math.log(statusnum + 1))
    return result


def get_day_activity_time(user_day_activity_time):
    results = {}
    activity_list_dict = {}  # {uid:[activity_list]}
    uid = user_day_activity_time["uid"]
    activity_list_dict[uid] = []

    for i in range(0, 96):
        try:
            count = user_day_activity_time["time_segment"][i]
        except:
            count = 0
        activity_list_dict[uid].append(count)
    # print (activity_list_dict)
    activity_list = activity_list_dict[uid]
    statusnum = sum(activity_list)

    signal = np.array(activity_list)

    fftResult = np.abs(np.fft.fft(signal)) ** 2
    n = signal.size
    freq = np.fft.fftfreq(n, d=1)
    i = 0
    max_val = 0
    max_freq = 0
    for val in fftResult:
        if val > max_val and freq[i] > 0:
            max_val = val
            max_freq = freq[i]
        i += 1

    results[uid] = {'statusnum': statusnum, 'activity_time': math.log(max_freq + 1)}

    return results




def search_es(uid):
    day_time = int(time.mktime(datetime.date.today().timetuple()))+86400
    pre_time = day_time - 86400 * 200
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "timestamp": {
                                "gt": pre_time,
                                "lt": day_time
                            }
                        }
                    }
                    ,
                    {
                        "term": {
                            "uid": uid
                        }
                    }
                    ,
                ],
                "must_not": [],
                "should": []
            }
        },
        "from": 0,
        "sort": [],
        "aggs": {}
    }
    query = es.search(index="weibo_all", body=query_body, scroll='5m', size=10000)
    results = query['hits']['hits']
    messages = []
    for line in results:
        messages.append(line['_source'])
    return messages

def cal_activityness(uid_list):
    activityness_dict = {}
    for uid in uid_list:
        data = search_es(uid)
        print(data)
        weibo_num = len(data)
        user_day_activeness_geo = {}
        if weibo_num:
            for weibo in data:
                geo = weibo['geo']
                if geo not in user_day_activeness_geo:
                    user_day_activeness_geo[geo] = 1
                else:
                    user_day_activeness_geo[geo] += 1
            activeness = get_day_activeness(user_day_activeness_geo,weibo_num, uid)
            activityness_dict[uid] = activeness
        else:
            activityness_dict[uid] = 0
    save_act(activityness_dict)
    return activityness_dict

def cal_sensitive(word_dict):
    sensitive_dict = {}
    uids = word_dict.keys()
    word_score = {}
    with open('word_score.txt', 'r', encoding='utf8') as f:
        for line in f.readlines():
            line = line.strip().split('\t')
            # print(line)
            word_score[line[0]] = int(line[1])
    for uid in uids:
        sensitiveness = 0
        for word in word_dict[uid].keys():
            if word in word_score.keys():
                sensitiveness += word_score[word]*word_dict[word]
        sensitive_dict[uid] = sensitiveness
    save_sen(sensitive_dict)
    return sensitive_dict

def save_act(dic):
    cursor = db.cursor()
    val = []
    sql = "INSERT INTO NewUserInfluence(uid_ts,uid,activity) VALUE(%s,%s,%s) ON DUPLICATE KEY UPDATE uid_ts= values(uid_ts),uid=values(uid),activity=values(activity)"
    for uid in dic.keys():
        uid_ts = uid + str(int(time.mktime(datetime.date.today().timetuple())))
        activity = dic[uid]
        val.append((uid_ts, uid, int(activity)))
        # % (uid_ts, uid, influence,uid_ts,uid,influence)  # timestamp between '%d'and '%d'，pretime,nowtime,
    try:
        cursor.executemany(sql,val)
        # 获取所有记录列表
        db.commit()
    except:
        print('cuowu')
        db.rollback()


def save_sen(dic):
    cursor = db.cursor()
    val = []
    sql = "INSERT INTO NewUserInfluence(uid_ts,uid,sensitity) VALUE(%s,%s,%s) ON DUPLICATE KEY UPDATE uid_ts= values(uid_ts),uid=values(uid),sensitity=values(sensitity)"
    for uid in dic.keys():
        uid_ts = uid + str(int(time.mktime(datetime.date.today().timetuple())))
        sensitity = dic[uid]
        val.append((uid_ts, uid, int(sensitity)))
        # % (uid_ts, uid, influence,uid_ts,uid,influence)  # timestamp between '%d'and '%d'，pretime,nowtime,
    try:
        cursor.executemany(sql,val)
        # 获取所有记录列表
        db.commit()
    except:
        print('错误')
        db.rollback()

if __name__ == '__main__':
    day_time = int(time.mktime(datetime.date.today().timetuple())) + 86400
    pre_time = day_time - 86400 * 2
    uid_list = ['1095184227']
    print(cal_activityness(uid_list))
    uid = '1095184227'
    wordcount = {}
    wordcount[uid] = json.loads(search_woordcount(uid, nowtime=day_time, pretime=pre_time)[0][0])
    print(cal_sensitive(wordcount))
    db.close()