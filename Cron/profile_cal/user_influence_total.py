from elasticsearch import Elasticsearch
import numpy as np
import pymysql
import datetime
import json
import math
import time

# from influence.Config import *
TOPIC_WEIGHT_DICT = {'topic_art': 0.2, 'topic_computer': 0.3*100000, 'topic_economic': 0.5, \
                     'topic_education': 0.5, 'topic_environment': 0.3, 'topic_medicine': 0.3, \
                     'topic_military': 0.8, 'topic_politics': 0.8, 'topic_sports': 0.2, \
                     'topic_traffic': 0.3, 'topic_life': 0.2, 'topic_anti_corruption': 0.8, \
                     'topic_employment': 0.5, 'topic_violence': 1, \
                     'topic_house': 0.4, 'topic_law': 0.7, 'topic_peace': 0.9, \
                     'topic_religion': 0.8, 'topic_social_security': 0.6, 'l':1 }

IMPORTANCE_WEIGHT_DICT = {'fansnum': 0.2, 'domain': 0.5, 'topic': 0.3}

DOMAIN_WEIGHT_DICT = {'university': 0.8, 'homeadmin': 0.6, 'abroadadmin': 1, 'homemedia': 1, \
                      'abroadmedia': 1, 'folkorg': 0.8, 'lawyer': 1, 'politician': 0.8, \
                      'mediaworker': 0.8, 'activer': 0.6, 'grassroot': 0.6, 'other': 0.5, 'business': 0.6}
activeness_weight_dict = { 'activity_geo': 0.5, 'statusnum': 0.5}

ES_HOST = '219.224.135.12'
ES_PORT = 9211

es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)
db = pymysql.connect(
    host='219.224.135.12',
    port=3306,
    user='root',
    passwd='mysql3306',
    db='PoliticalInfiltration',
    charset='utf8'
)
'''
影响力依赖统计
'''
def querry(field,root_uid,type):
    querrybody = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            field: root_uid
                        }
                    }
                    ,
                    {
                        "term": {
                            "message_type": type
                        }
                    }
                ],
                "must_not": [],
                "should": []
            }
        },
        "from": 0,
        "size": 10,
        "sort": [],
        "aggs": {}
    }
    query = es.search(index="weibo_all", body=querrybody, scroll='5m', size=10000)

    results = query['hits']['hits']  # es查询出的结果第一页
    total = query['hits']['total']  # es查询出的结果总量
    scroll_id = query['_scroll_id']  # 游标用于输出es查询出的所有结果
    list = []
    for line in results:
        list.append(line['_source'])
    for i in range(0, int(total / 10000) + 1):
        # scroll参数必须指定否则会报错
        query_scroll = es.scroll(scroll_id=scroll_id, scroll='5m')['hits']['hits']

        for line in query_scroll:
            list.append(line['_source'])
        yield list

def get_queue_index(timestamp):
    time_struc = time.gmtime(float(timestamp))
    hour = time_struc.tm_hour
    minute = time_struc.tm_min
    index = hour * 4 + math.ceil(minute / 15.0)  # every 15 minutes
    return int(index)


def statistics(uid_list):
    tart_time = time.time()

    o_save_dict = dict()
    for uid in uid_list:
        o_save_dict[uid] = dict()
        o_save_dict[uid]['or_act'] = dict()
        o_save_dict[uid]['oc_act'] = dict()
        for i in range(0, 97):
            o_save_dict[uid]['or_act'][i] = 0
            o_save_dict[uid]['oc_act'][i] = 0
    start_time = time.time()
    num = 0
    for uid in uid_list:
        # print(uid)
        o_mid = []
        for list in querry("uid", uid, 1):
            print(len(list))
            for message in list:
                # print(message)
                o_mid.append((message['mid'], message['timestamp'], message['time']))
        # print(o_mid)
        for tuple in o_mid:
            mid = tuple[0]
            # print(mid)
            o_save_dict[uid][mid] = dict()
            o_save_dict[uid][mid]['timestamp'] = tuple[1]
            o_save_dict[uid][mid]['date'] = tuple[2]
            for list in querry("root_mid", mid, 2):
                o_save_dict[uid][mid]['comment'] = len(list)
                for message in list:
                    index = get_queue_index(message['timestamp'])
                    # print(o_save_dict[uid]['oc_act'])
                    o_save_dict[uid]['oc_act'][index] += 1
                    # try:
                    #     o_save_dict[uid][mid]['comment'] += 1
                    # except:
                    #     o_save_dict[uid][mid]['comment'] = 1

            for list in querry("root_mid", mid, 3):
                # print(len(list))
                o_save_dict[uid][mid]['retweet'] = len(list)
                for message in list:
                    index = get_queue_index(message['timestamp'])
                    o_save_dict[uid]['or_act'][index] += 1

        oc_index_l = o_save_dict[uid]['oc_act'].values()
        max_oc_index = max(oc_index_l)
        oc_activite_time_num = 0
        active_act_num = 0
        for i in oc_index_l:
            if i > int(max_oc_index / 2) + 1 and i > 5:
                oc_activite_time_num += 1
                active_act_num += i
        try:
            oc_ev_av_num = int(active_act_num / oc_activite_time_num)
        except:
            oc_ev_av_num = 0
        o_save_dict[uid]['oc_act']['oc_activite_time_num'] = oc_activite_time_num
        o_save_dict[uid]['oc_act']['oc_ac_av_num'] = oc_ev_av_num

        or_index_l = o_save_dict[uid]['or_act'].values()
        max_or_index = max(or_index_l)
        or_activite_time_num = 0
        active_act_num = 0
        for i in or_index_l:
            if i > int(max_oc_index / 2) + 1 and i > 5:
                or_activite_time_num += 1
                active_act_num += i
        try:
            or_ev_av_num = int(active_act_num / or_activite_time_num)
        except:
            or_ev_av_num = 0
        o_save_dict[uid]['or_act']['or_activite_time_num'] = or_activite_time_num
        o_save_dict[uid]['or_act']['or_ac_av_num'] = or_ev_av_num

        num += 1
        # print(num)
        # if num % 1000 == 0:
        #     print(time.time() - start_time)


    cursor = db.cursor()
    with open('uid.txt', 'w', encoding='utf8') as wf:
        for uid in o_save_dict.keys():
            wf.write(uid + '\n')

    for uid in o_save_dict.keys():
        # print(uid)
        try:
            for mid in o_save_dict[uid].keys():
                if mid != 'or_act' and mid != 'oc_act':
                    # print(mid)
                    data = []
                    # print(o_save_dict[uid][mid])
                    value = (uid, mid, int(o_save_dict[uid][mid]['retweet']),
                             int(o_save_dict[uid][mid]['comment']), int(o_save_dict[uid][mid]['timestamp']),
                             int(o_save_dict[uid]['or_act']['or_activite_time_num']),
                             int(o_save_dict[uid]['or_act']['or_ac_av_num']),
                             int(o_save_dict[uid]['oc_act']['oc_activite_time_num']),
                             int(o_save_dict[uid]['oc_act']['oc_ac_av_num']), o_save_dict[uid][mid]['date'])

                    data.append(value)
                    sql = "insert into Influence(uid, mid,retweeted,comment,timestamp,original_retweeted_time_num,original_retweeted_average_num," \
                          "original_comment_time_num,original_comment_average_num,date) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s )"
                    # print(data)
                    cursor.executemany(sql, data)
        except:
            continue
    db.commit()

'''
影响力计算
'''
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







def get_influence_dict(uid_list):

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
        result_dict[uid]['influence'] = influence

'''
重要度计算
'''

def search_domain(uid,nowtime,pretime):
    cursor = db.cursor()
    sql = "SELECT main_domain FROM  UserDomain  WHERE timestamp between '%d'and '%d'and uid = '%s' order by timestamp desc limit 1" % (pretime,nowtime,uid)#timestamp between '%d'and '%d'，pretime,nowtime,
    # try:
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    return results

def search_topic(uid,nowtime,pretime):
    cursor = db.cursor()
    sql = "SELECT topics FROM  UserTopic  WHERE timestamp between '%d'and '%d'and uid = '%s' order by timestamp desc limit 1" % (
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
    domain_result = DOMAIN_WEIGHT_DICT[domain]*1
    # print(domain_result)
    topic_result = 0
    for topic in topic_dict.keys():
        try :
            # print(topic_result)
            topic_result += topic_dict[topic]*TOPIC_WEIGHT_DICT['topic_'+topic]
        except :
            continue
    # print(  fansnum_max)
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
    max_fans_num = get_max_fansnum()
    for uid in uid_list:
        try:
            domains = search_domain(uid,nowtime=day_time,pretime=pre_time)[0]
            # print(domains)
            domain = domains[0]
            # domains_dict = {}
            # for i in domain_list:
            #     domains_dict[i[0]]=i[1]
            topics = search_topic(uid, nowtime=day_time, pretime=pre_time)[0]
            topic_list = json.loads(topics[0])
            # print(topic_list)
            # topics_dict = {}
            # for i in topic_list:
            #     topics_dict[i[0]] = i[1]
            # # print(topics_dict)
            fansnum = get_fansnum(uid)
            # print(topics_dict)
            # print(topic_list)
            importance = cal_importance(domain=domain,topic_dict=topic_list,user_fansnum=fansnum,fansnum_max=max_fans_num)
            result_dict[uid]['importance']=importance
        except:
            result_dict[uid]['importance'] = 0

'''
计算敏感度和活跃度
'''
def search_woordcount(uid,nowtime,pretime):
    cursor = db.cursor()
    sql = "SELECT wordcount FROM  WordCount  WHERE timestamp between '%d'and '%d'and uid = '%s' " % (pretime,nowtime,uid)#timestamp between '%d'and '%d'，pretime,nowtime,
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

def get_activityness_dict(uid_list):
    for uid in uid_list:
        data = search_es(uid)
        # print(data)
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
            result_dict[uid]['activity'] = activeness*100
        else:
            result_dict[uid]['activity'] = 0


def get_sensitive_dict(word_dict):
    uids = word_dict.keys()
    word_score = {}
    with open('word_score.txt', 'r', encoding='utf8') as f:#D:\PycharmProjects\zzst\influence\
        for line in f.readlines():
            line = line.strip().split('\t')
            # print(line)
            word_score[line[0]] = int(line[1])
    num = 0
    sensitive_word = word_score.keys()
    for uid in uids:
        sensitiveness = 0
        for day_dic in word_dict[uid]:
            for word in day_dic.keys():
                if word in sensitive_word:
                    sensitiveness += word_score[word]*day_dic[word]
        num +=1
        print(num)
        result_dict[uid]['sensitive'] = sensitiveness

'''
存储计算结果
'''
def influence_total(uid_list,start_date,end_date):
    global day_time
    # day_time = int(time.mktime(datetime.date.today().timetuple()))+86400
    day_time =int(time.mktime(time.strptime(end_date, "%Y-%m-%d")))
    global pre_time
    pre_time = int(time.mktime(time.strptime(start_date, "%Y-%m-%d")))
    # pre_time = day_time - 86400 * 200
    global result_dict
    result_dict = {}

    for uid in uid_list:
        result_dict[uid] = {}
    statistics(uid_list)
    get_influence_dict(uid_list)
    get_importance_dic(uid_list)
    get_activityness_dict(uid_list)

    wordcount = {}
    for uid in uid_list:
        worddict_list = []
        try:
            for i in search_woordcount(uid, nowtime=day_time, pretime=pre_time):
                worddict_list.append(json.loads(i[0]))
            wordcount[uid] = worddict_list
            # wordcount[uid] = json.loads(search_woordcount(uid, nowtime=day_time, pretime=pre_time)[0][0])
        except:
            wordcount[uid] = {}
            continue
    get_sensitive_dict(wordcount)

    save_sql(result_dict)


def save_sql(dic):
    cursor = db.cursor()
    val = []
    sql = "INSERT INTO NewUserInfluence(uid_ts,uid,sensitity,activity,importance,influence,timestamp,store_date) VALUE(%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE uid_ts= values(uid_ts" \
          "),uid=values(uid),sensitity=values(sensitity),importance=values(importance),activity=values(activity),influence=values(influence),timestamp=values(timestamp ),store_date = values(store_date)"
    timestamp = int(day_time)
    store_time = datetime.date.today()
    for uid in dic.keys():
        uid_ts = uid + str(int(time.mktime(datetime.date.today().timetuple())))
        sensitity = dic[uid]['sensitive']
        activity = dic[uid]['activity']
        importance = dic[uid]['importance']
        influence = dic[uid]['influence']
        val.append((uid_ts, uid, int(sensitity),int(activity),int(importance),int(influence),timestamp,store_time))
        # % (uid_ts, uid, influence,uid_ts,uid,influence)  # timestamp between '%d'and '%d'，pretime,nowtime,
    try:
        cursor.executemany(sql,val)
        # 获取所有记录列表
        db.commit()
    except:
        print('错误')
        db.rollback()
    db.close()



