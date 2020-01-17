import time
import math
import datetime
import pymysql
from elasticsearch import Elasticsearch


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

def search(uid,nowtime,pretime):
    cursor = db.cursor()
    sql = "SELECT * FROM  Influence  WHERE timestamp between '%d'and '%d'and uid = '%s'" % (pretime,nowtime,uid)#timestamp between '%d'and '%d'，pretime,nowtime,
    # try:
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    return results
    # except:
    #     return None

def activity_influence(total,ave,max,ac_num,av_ac_num):
    influence = 0.5*math.log(total+1,math.e)+0.2*math.log(ave+1,math.e)+0.1*math.log(max+1,math.e)+\
                0.1*math.log(ac_num+1,math.e)+0.1*math.log(av_ac_num+1,math.e)
    return influence

def user_influence(uid,or_influence,oc_influence,pre_time,day_time):
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
                    {
                        "term": {
                            "message_type": 1
                        }
                    }
                ],
                "must_not": [],
                "should": []
            }
        },
        "from": 0,
        "sort": [],
        "aggs": {}
    }

    query = es.search(index="weibo_all", body=query_body,scroll='5m', size=10000)
    o_num = query['hits']['total']


    query_body1 = {
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
                    {
                        "term": {
                            "message_type": 3
                        }
                    }
                ],
                "must_not": [],
                "should": []
            }
        },
        "from": 0,
        "sort": [],
        "aggs": {}
    }
    query = es.search(index="weibo_all", body=query_body1,scroll='5m', size=10000 )
    r_num = query['hits']['total']

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
        "sort":{
            "timestamp":{
                "order":"desc"
            }
        },
        "aggs": {}
    }
    result = es.search(index="weibo_all", body=query_body2, scroll='5m', size=1)['hits']['hits']
    if len(result)==0:
        fans_num = 0
    else:
        print(result)
        for line in result:
            fans_num = line['_source']['user_fansnum']
    user_influence = (0.15*(0.6*math.log(o_num+1,math.e)+0.3*math.log(r_num+1,math.e)+0.1*math.log(fans_num+1,math.e))+
                      0.85*(0.5*or_influence+0.5*oc_influence))*300
    return user_influence







def total_influence(uid_list):
    day_time = int(time.mktime(datetime.date.today().timetuple()))
    pre_time = day_time - 86400 * 15
    influence_dic = {}
    # uids = []
    # with open("uid.txt", 'r', encoding='utf8') as f:
    #     for line in f.readlines():
    #         uids.append(line.strip())
    for uid in uid_list:
        # print(uid)
        influence = 0
        results = search(uid,pre_time,day_time)
        if len(results) == 0:
            or_influence = 0
            oc_influence = 0
        else:
            line_statistic = {}
            for line in results:
                try:
                    line_statistic['total_comment'] += line[2]
                    line_statistic['total_retweet'] += line[3]
                    line_statistic['original_retweeted_time_num'] += line[4]
                    line_statistic['original_comment_time_num'] += line[5]
                    line_statistic['original_retweeted_average_num'] += line[6]
                    line_statistic['original_comment_average_num'] += line[7]
                    if line[2]>line_statistic['max_comment']:
                        line_statistic['max_comment'] = line[2]
                    if line[2]>line_statistic['max_retweet']:
                        line_statistic['max_retweet'] = line[3]
                except:
                    line_statistic['total_comment'] = 0
                    line_statistic['total_retweet'] = 0
                    line_statistic['original_retweeted_time_num'] = 0
                    line_statistic['original_comment_time_num'] = 0
                    line_statistic['original_retweeted_average_num'] = 0
                    line_statistic['original_comment_average_num'] = 0
                    line_statistic['max_comment'] = 0
                    line_statistic['max_retweet'] = 0
                    line_statistic['av_comment'] = 0
                    line_statistic['av_retweet'] = 0
                line_statistic['av_comment'] = line_statistic['total_comment']/len(results)
                line_statistic['av_retweet'] = line_statistic['total_retweet']/len(results)
            or_influence = activity_influence(line_statistic['total_retweet'],line_statistic['av_retweet'],line_statistic['max_retweet'],
                                              line_statistic['original_retweeted_time_num'],line_statistic['original_retweeted_average_num'])
            oc_influence = activity_influence(line_statistic['total_comment'],line_statistic['av_comment'],line_statistic['max_comment'],
                                              line_statistic['original_comment_time_num'],line_statistic['original_comment_average_num'])
        influence = user_influence(uid,or_influence,oc_influence,pre_time=pre_time,day_time=day_time)
        influence_dic[uid] = influence
    print(influence_dic)
    save(influence_dic)
    return influence_dic

def save(dic):
    cursor = db.cursor()
    val = []
    sql = "INSERT INTO NewUserInfluence(uid_ts,uid,influence) VALUE(%s,%s,%s) ON DUPLICATE KEY UPDATE uid_ts= values(uid_ts),uid=values(uid),influence=values(influence)"
    for uid in dic.keys():
        uid_ts = uid + str(int(time.mktime(datetime.date.today().timetuple())))
        influence = dic[uid]
        val.append((uid_ts, uid, int(influence)))
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
    uid_list = ['1794541877']
    total_influence(uid_list)
