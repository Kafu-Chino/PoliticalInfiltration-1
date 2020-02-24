from elasticsearch import Elasticsearch
import numpy as np
import pymysql
import datetime
import json
import math
import time

from Config.db_utils import es,conn,pi_cur
from Config.time_utils import *

# from influence.Config import *
TOPIC_WEIGHT_DICT = {'topic_art': 0.2, 'topic_computer': 0.3*1, 'topic_economic': 0.5, \
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
def connect():
    es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)
    db = pymysql.connect(
        host='219.224.135.12',
        port=3306,
        user='root',
        passwd='mysql3306',
        db='PoliticalInfiltration',
        charset='utf8'
    )
    return es,db
'''
影响力依赖统计
'''
def querry(field,root_uid,type,index,days):
    querrybody = {
        "query": {
            "bool": {
                "must": [
                    # {
                    #     "range": {
                    #         "timestamp": {
                    #             "gt": day_time-86400*days,
                    #             "lt": day_time
                    #         }
                    #     }
                    # },
                    {
                        "terms": {
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
        "sort": [],
        "aggs": {}
    }
    # print(index)
    query = es.search(index=index, body=querrybody, scroll='5m', size=10000)

    results = query['hits']['hits']  # es查询出的结果第一页
    total = query['hits']['total']  # es查询出的结果总量
    scroll_id = query['_scroll_id']  # 游标用于输出es查询出的所有结果
    list = []
    for line in results:
        list.append(line['_source'])
    yield list
    for i in range(0, int(total / 10000) + 1):
        # scroll参数必须指定否则会报错
        query_scroll = es.scroll(scroll_id=scroll_id, scroll='5m')['hits']['hits']
        list = []
        for line in query_scroll:
            list.append(line['_source'])
        yield list

def get_mid_list(uid_list):
    cursor = pi_cur()
    uids = ''
    for uid in uid_list:
        uids += uid + ','
    sql = 'select mid,uid,timestamp,date,comment,retweeted from Influence where uid in (%s) and timestamp >=%d and timestamp<%d'%(uids[:-1],day_time-7*86400,day_time-86400)
    cursor.execute(sql)
    results = cursor.fetchall()
    return results

def get_queue_index(timestamp):
    time_struc = time.gmtime(float(timestamp))
    hour = time_struc.tm_hour
    minute = time_struc.tm_min
    index = hour * 4 + math.ceil(minute / 15.0)  # every 15 minutes
    return int(index)


def statistics(uid_list,index1):
    s_time = time.time()
    o_save_dict = dict()
    for uid in uid_list:
        o_save_dict[uid] = dict()
        o_save_dict[uid]['or_act'] = dict()
        o_save_dict[uid]['oc_act'] = dict()
        for i in range(0, 97):
            o_save_dict[uid]['or_act'][i] = 0
            o_save_dict[uid]['oc_act'][i] = 0

    uid_o_mid = {}
    for uid in uid_list:
        uid_o_mid[uid] = []
    for list in querry("uid", uid_list, 1,index1,1):
        for message in list:
            # if message['uid'] in uid_o_mid.keys():
            uid_o_mid[message['uid']].append((message['mid'], message['timestamp'], ts2date(message['timestamp'])))
    # print(time.time()-s_time)
    for message in get_mid_list(uid_list):
        uid_o_mid[message['uid']].append((message['mid'], message['timestamp'], message['date'],message['comment'],message['retweeted']))
    # print(time.time()-s_time)
    mid_list = []
    for uid in uid_list:
        o_mid = uid_o_mid[uid]
        mids = []
        for tuple in o_mid:
            if len(tuple)==3:
                mid = tuple[0]
                mid_list.append(mid)
                mids.append(mid)
                o_save_dict[uid][mid] = dict()
                o_save_dict[uid][mid]['comment'] = 0
                o_save_dict[uid][mid]['retweet'] = 0
            else:
                mid = tuple[0]
                mid_list.append(mid)
                mids.append(mid)
                o_save_dict[uid][mid] = dict()
                o_save_dict[uid][mid]['comment'] = tuple[3]
                o_save_dict[uid][mid]['retweet'] = tuple[4]
        for tuple in o_mid:
            # mid = tuple[0]
            # o_save_dict[uid][mid] = dict()
            o_save_dict[uid][tuple[0]]['timestamp'] = tuple[1]
            o_save_dict[uid][tuple[0]]['date'] = str(tuple[2])[:10]
    # print(time.time() - s_time)
    querry_list = querry("root_mid", mid_list, 2,index1,1)
    # print(time.time() - s_time)
    for list1 in querry_list:
        # o_save_dict[uid][mid]['comment'] = len(list)
        for message in list1:
            try:
                o_save_dict[message['root_uid']][message['root_mid']]['comment'] += 1
                index = get_queue_index(message['timestamp'])
                o_save_dict[message['root_uid']]['oc_act'][index] += 1
            except:
                continue
    # print(time.time() - s_time)
    querry_list = querry("root_mid",  mid_list, 3,index1,1)
    # print(time.time() - s_time)
    for list1 in querry_list:
        # print(len(list1))
        for message in list1:
            try:
                o_save_dict[message['root_uid']][message['root_mid']]['retweet'] += 1
                index = get_queue_index(message['timestamp'])
                o_save_dict[message['root_uid']]['or_act'][index] += 1
            except:
                continue
    # print(time.time() - s_time)

    for uid in uid_list:
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
            if i > int(max_or_index / 2) + 1 and i > 5:
                or_activite_time_num += 1
                active_act_num += i
        try:
            or_ev_av_num = int(active_act_num / or_activite_time_num)
        except:
            or_ev_av_num = 0
        o_save_dict[uid]['or_act']['or_activite_time_num'] = or_activite_time_num
        o_save_dict[uid]['or_act']['or_ac_av_num'] = or_ev_av_num

    cursor = db.cursor()
    data = []
    sql = "insert into Influence(uid, mid,retweeted,comment,timestamp,original_retweeted_time_num,original_retweeted_average_num," \
          "original_comment_time_num,original_comment_average_num,date) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s )" \
          "ON DUPLICATE KEY UPDATE uid=values(uid),mid=values(mid),retweeted=values(retweeted),comment=values(comment),timestamp=values(timestamp)," \
          "original_retweeted_time_num=values(original_retweeted_time_num),original_retweeted_average_num=values(original_retweeted_average_num)," \
          "original_comment_time_num=values(original_comment_time_num),original_comment_average_num=values(original_comment_average_num),date=values(date)"

    for uid in o_save_dict.keys():
        for mid in o_save_dict[uid].keys():
            if mid != 'or_act' and mid != 'oc_act':

                value = (uid, mid, int(o_save_dict[uid][mid]['retweet']),
                         int(o_save_dict[uid][mid]['comment']), int(o_save_dict[uid][mid]['timestamp']),
                         int(o_save_dict[uid]['or_act']['or_activite_time_num']),
                         int(o_save_dict[uid]['or_act']['or_ac_av_num']),
                         int(o_save_dict[uid]['oc_act']['oc_activite_time_num']),
                         int(o_save_dict[uid]['oc_act']['oc_ac_av_num']), o_save_dict[uid][mid]['date'])

                data.append(value)
    cursor.executemany(sql, data)

    db.commit()


'''
影响力计算
'''
def search(uid,nowtime,pretime):
    cursor = db.cursor()
    sql = "SELECT * FROM  Influence  WHERE timestamp between '%d'and '%d'and uid = '%s'" % (pretime,nowtime,uid)#timestamp between '%d'and '%d'，pretime,nowtime,
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    return results


def activity_influence(total,ave,max,ac_num,av_ac_num):
    influence = 0.5*math.log(total+1,math.e)+0.2*math.log(ave+1,math.e)+0.1*math.log(max+1,math.e)+\
                0.1*math.log(ac_num+1,math.e)+0.1*math.log(av_ac_num+1,math.e)
    return influence


# def querry2(field,uid_list,index):
#     querrybody = {
#         "query": {
#             "bool": {
#                 "must": [
#                     # {
#                     #     "range": {
#                     #         "timestamp": {
#                     #             "gt": pre_time,
#                     #             "lt": day_time
#                     #         }
#                     #     }
#                     # },
#                     {
#                         "terms": {
#                             field: uid_list
#                         }
#                     },
#                 ],
#                 "must_not": [],
#                 "should": []
#             }
#         },
#         "from": 0,
#         "size": 10000,
#         "sort":{
#             "timestamp":{
#                 "order":"desc"
#             }
#         },
#         "aggs": {}
#     }
#     query = es.search(index=index, body=querrybody, scroll='5m', size=10000)
#
#     results = query['hits']['hits']  # es查询出的结果第一页
#     total = query['hits']['total']  # es查询出的结果总量
#     scroll_id = query['_scroll_id']  # 游标用于输出es查询出的所有结果
#     list = []
#     for line in results:
#         list.append(line['_source'])
#     for i in range(0, int(total / 10000) + 1):
#         # scroll参数必须指定否则会报错
#         query_scroll = es.scroll(scroll_id=scroll_id, scroll='5m')['hits']['hits']
#
#         for line in query_scroll:
#             list.append(line['_source'])
#         yield list


def user_influence(or_influence,oc_influence,o_num,r_num,fans_num):
    user_influence = (0.15*(0.6*math.log(o_num+1,math.e)+0.3*math.log(r_num+1,math.e)+0.1*math.log(fans_num+1,math.e))+
                      0.85*(0.5*or_influence+0.5*oc_influence))*300
    return user_influence



def get_influence_dict(uid_list,data):
    for uid in uid_list:
        statistic[uid] = {}
        statistic[uid]['fansnum'] = 0
        statistic[uid]['original'] = 0
        statistic[uid]['retweet'] = 0
    # for list in querry2("uid", uid_list,index):
    for uid in data:
        for message in data[uid]:
            if message['message_type'] == 1:
                statistic[message['uid']]['original'] += 1
            if message['message_type'] == 3:
                statistic[message['uid']]['retweet'] += 1
            statistic[message['uid']]['fansnum'] += message['user_fansnum']

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

        influence = user_influence(or_influence=or_influence,oc_influence=oc_influence,o_num=statistic[uid]['original'],r_num=statistic[uid]['retweet'],fans_num=statistic[uid]['fansnum'])
        if influence/1.2>100:
            influence=100
        else:
            influence = influence/1.2
        result_dict[uid]['influence'] = influence

'''
重要度计算
'''
def get_domain_topic(uid_list,day_timestamp):
    cursor = db.cursor()
    uids = ''
    for uid in uid_list:
        uids += uid + ','

    sql = "select uid,main_domain from UserDomain where  uid in (%s) and timestamp = %d" % (uids[:-1], day_timestamp)

    # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    results = cursor.fetchall()

    cursor = db.cursor()
    sql = "select uid,topics from UserTopic where  uid in (%s)and timestamp = %d" % (uids[:-1], day_timestamp)
    cursor.execute(sql)
    # 提交到数据库执行
    results1 = cursor.fetchall()
    domain_topic_dict = {}
    for uid in uid_list:
        domain_topic_dict[uid] = dict()
        domain_topic_dict[uid]['main_domain'] = 0
        domain_topic_dict[uid]['topic'] = 0
    # 关闭数据库连接
    for m in results:
        domain_topic_dict[m[0]]['main_domain'] = m[1]
    for m in results1:
        domain_topic_dict[m[0]]['topic'] = json.loads(m[1])
    return domain_topic_dict


def get_max_fansnum(index):
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
    query = es.search(index=index, body=query_body, scroll='5m', size=1)

    results = query['hits']['hits']  # es查询出的结果第一页
    for line in results:
        max_fansnum = line["_source"]['user_fansnum']

    return max_fansnum

def cal_importance(domain, topic_dict, user_fansnum, fansnum_max):
    domain_result = 0
    if domain!=0:
        domain_result = DOMAIN_WEIGHT_DICT[domain]*1
    topic_result = 0
    if topic_dict != 0:
        for topic in topic_dict.keys():
            try :
                # print(topic_result)
                topic_result += topic_dict[topic]*TOPIC_WEIGHT_DICT['topic_'+topic]
            except :
                continue
    # print(topic_result,domain_result,user_fansnum)
    result = (IMPORTANCE_WEIGHT_DICT['fansnum']*math.log(float(user_fansnum)/ fansnum_max*9+1, 10) +
            IMPORTANCE_WEIGHT_DICT['domain']*domain_result +
              IMPORTANCE_WEIGHT_DICT['topic']*(topic_result / 3))*1000
    return result


# 1579177125
def get_importance_dic(uid_list,index):
    max_fans_num = get_max_fansnum(index)
    domain_topic = get_domain_topic(uid_list,day_time-86400)
    for uid in uid_list:
        try:
            domain = domain_topic[uid]['main_domain']
            topics = domain_topic[uid]['topic']
            # fansnum = get_fansnum(uid)
            importance = cal_importance(domain=domain,topic_dict=topics,user_fansnum=statistic[uid]['fansnum'],fansnum_max=max_fans_num)
            if importance>100:
                importance = 100
            result_dict[uid]['importance']=importance
        except:
            print('错误')
            result_dict[uid]['importance'] = 0

'''
计算敏感度和活跃度
'''

def get_day_activeness(user_day_activeness_geo,weibo_num, uid):
    result = 0
    # get day geo dict by ip-timestamp result

    statusnum = weibo_num
    activity_geo_count = len(user_day_activeness_geo.keys())
    result = int(activeness_weight_dict['activity_geo'] * math.log(activity_geo_count*100 + 1) + \
                 activeness_weight_dict['statusnum'] * math.log(statusnum*100 + 1))
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


def get_activityness_dict(uid_list,date_data):
    for uid in uid_list:
        if uid in date_data.keys():
            data = date_data[uid]
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
                if activeness>100:
                    activeness = 100
                result_dict[uid]['activity'] = activeness*1
            else:
                result_dict[uid]['activity'] = 0
        else:
            result_dict[uid]['activity'] = 0


def get_sensitive_dict(uid_list,word_dict):
    uids = uid_list
    word_score = {}
    with open('word_score.txt', 'r', encoding='utf8') as f:#D:\PycharmProjects\zzst\influence\
        for line in f.readlines():
            line = line.strip().split('\t')
            word_score[line[0]] = int(line[1])
    # num = 0
    sensitive_word = word_score.keys()
    for uid in uids:
        sensitiveness = 0
        # for day_dic in word_dict[uid]:
        if uid in word_dict.keys():
            for word in word_dict[uid].keys():
                if word in sensitive_word:
                    sensitiveness += word_score[word]*word_dict[uid][word]
        if sensitiveness>100:
            sensitiveness=100
        result_dict[uid]['sensitive'] = sensitiveness

'''
存储计算结果
'''
def influence_total(date,uid_list,word_count,data,index):
    start_time = time.time()
    global store_date
    store_date = date
    global es
    global db
    es,db = connect()
    global day_time
    # day_time = int(time.mktime(datetime.date.today().timetuple()))+86400
    day_time =int(time.mktime(time.strptime(date, "%Y-%m-%d")))+86400
    global pre_time
    # pre_time = int(time.mktime(time.strptime(start, "%Y-%m-%d")))
    pre_time = day_time - 86400 * 14
    global result_dict
    result_dict = {}
    global statistic
    statistic = {}

    for uid in uid_list:
        result_dict[uid] = {}
    statistics(uid_list,index)
    # print(time.time()-start_time)
    get_influence_dict(uid_list,data)
    # print(time.time() - start_time)
    get_importance_dic(uid_list,index)
    # print(time.time() - start_time)
    get_activityness_dict(uid_list,data)
    # print(time.time() - start_time)
    get_sensitive_dict(uid_list,word_count)
    # print(time.time() - start_time)

    save_sql(result_dict)


def save_sql(dic):
    cursor = db.cursor()
    val = []
    sql = "INSERT INTO NewUserInfluence(uid_ts,uid,sensitity,activity,importance,influence,timestamp,store_date) VALUE(%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE uid_ts= values(uid_ts" \
          "),uid=values(uid),sensitity=values(sensitity),importance=values(importance),activity=values(activity),influence=values(influence),timestamp=values(timestamp ),store_date = values(store_date)"
    timestamp = int(day_time)
    store_time = store_date
    for uid in dic.keys():
        # uid_ts = uid + str(int(time.mktime(datetime.date.today().timetuple())))
        uid_ts = uid + str(day_time-86400)
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

