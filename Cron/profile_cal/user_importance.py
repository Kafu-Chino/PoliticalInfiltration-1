import math
import time
import datetime
import pymysql
import json
from elasticsearch import Elasticsearch
from influence.Config import *



ES_HOST = '219.224.134.214'
ES_PORT = 9211
es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)
db = pymysql.connect(
        host='219.224.134.214',
        port=3306,
        user='root',
        passwd='mysql3306',
        db='PoliticalInfiltration',
        charset='utf8'
    )
def search_domain(uid,nowtime,pretime):
    cursor = db.cursor()
    sql = "SELECT main_domain FROM  UserDomain  WHERE timestamp between '%d'and '%d'and uid = '%s' limit 1" % (pretime,nowtime,uid)#timestamp between '%d'and '%d'，pretime,nowtime,
    # try:
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    return results

def search_topic(uid,nowtime,pretime):
    cursor = db.cursor()
    sql = "SELECT topics FROM  UserTopic  WHERE timestamp between '%d'and '%d'and uid = '%s' limit 1" % (
    pretime, nowtime, uid)  # timestamp between '%d'and '%d'，pretime,nowtime,
    # try:
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    return results


def get_max_fansnum():
    query_body = {
        "query": {
            "match_all": {},
        },
        "sort": {
            "user_fansnum": {
                "order": "desc"
            }
        },
    }
    # uid_list = ["2396658275"]
    query = es.search(index="weibo_all", body=query_body, scroll='5m', size=1)

    results = query['hits']['hits']  # es查询出的结果第一页
    for line in results:
        max_fansnum = line["_source"]['user_fansnum']

    return max_fansnum

def cal_importance(domain, topic_dict, user_fansnum, fansnum_max):
    result = 0
    domain_result = 0
    domain_result = DOMAIN_WEIGHT_DICT[domain]
    print(domain_result)
    topic_result = 0
    try :
        for topic in topic_dict.keys():
            topic_result += topic_dict[topic]*TOPIC_WEIGHT_DICT[topic]
    except :
        topic_result = 0
    print(  fansnum_max)
    result = (IMPORTANCE_WEIGHT_DICT['fansnum']*math.log(float(user_fansnum)/ fansnum_max*9+1, 10) +
            IMPORTANCE_WEIGHT_DICT['domain']*domain_result +
              IMPORTANCE_WEIGHT_DICT['topic']*(topic_result / 3))*100
    return result

def get_fansnum(uid):
    query_body2 = {
        "query": {
            "bool": {
                "must": [

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
        "sort": {
            "timestamp": {
                "order": "desc"
            }
        },
        "aggs": {}
    }
    result = es.search(index="weibo_all", body=query_body2, scroll='5m', size=1)['hits']['hits']
    if len(result) == 0:
        fans_num = 0
    else:
        for line in result:
            fans_num = line['_source']['user_fansnum']
    return fans_num
# 1579177125
def get_importance_dic(uid_list):
    day_time = int(time.mktime(datetime.date.today().timetuple()))+86400
    pre_time = day_time - 86400 * 2
    print(day_time,pre_time)
    importance_dic = {}
    max_fans_num = get_max_fansnum()
    for uid in uid_list:
        domains = search_domain(uid,nowtime=day_time,pretime=pre_time)[0]
        # print(domains)
        domain = domains[0]
        # domains_dict = {}
        # for i in domain_list:
        #     domains_dict[i[0]]=i[1]
        topics = search_topic(uid, nowtime=day_time, pretime=pre_time)[0]
        topic_list = json.loads(topics[0])
        topics_dict = {}
        for i in topic_list:
            topics_dict[i[0]] = i[1]
        fansnum = get_fansnum(uid)
        print(topics_dict)
        importance = cal_importance(domain=domain,topic_dict=topics_dict,user_fansnum=fansnum,fansnum_max=max_fans_num)
        importance_dic[uid]=importance
    save(importance_dic)
    return importance_dic

def save(dic):
    cursor = db.cursor()
    val = []
    sql = "INSERT INTO NewUserInfluence(uid_ts,uid,importance) VALUE(%s,%s,%s) ON DUPLICATE KEY UPDATE uid_ts= values(uid_ts),uid=values(uid),influence=values(importance)"
    for uid in dic.keys():
        uid_ts = uid + str(int(time.mktime(datetime.date.today().timetuple())))
        importance = dic[uid]
        val.append((uid_ts, uid, int(importance)))
        # % (uid_ts, uid, influence,uid_ts,uid,influence)  # timestamp between '%d'and '%d'，pretime,nowtime,
    try:
        cursor.executemany(sql,val)
        # 获取所有记录列表
        db.commit()
    except:
        print('cuowu')
        db.rollback()
    db.close()
if __name__ == '__main__':
    uid_list = ['1225869460']
    print(get_importance_dic(uid_list))
