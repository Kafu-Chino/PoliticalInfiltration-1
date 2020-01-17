from elasticsearch import Elasticsearch
import math
import pymysql
import multiprocessing
import random
import time
import redis


ES_HOST = '219.224.134.214'
ES_PORT = 9211

es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)

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
    index = hour*4+math.ceil(minute/15.0) #every 15 minutes
    return int(index)

# def save():



def statistics(uid_list):
    tart_time = time.time()
    uid_uname_dict = {}
    # uids = []
    # uname = []
    # with open("D:\\PycharmProjects\\zzst\\java对接\\uid_uname.txt", 'r', encoding='utf8') as f:
    #     for line in f.readlines():
    #         line = line.strip()
    #         line_list = line.split('\t')
    #         uid_uname_dict[line_list[0]] = line_list[1]
    #         # uname.append(line_list[0])
    #         uids.append(line_list[1])

    o_save_dict = dict()
    for uid in uid_list:
        o_save_dict[uid] = dict()
        o_save_dict[uid]['or_act'] = dict()
        o_save_dict[uid]['oc_act'] = dict()
        for i in range(1,97):
            o_save_dict[uid]['or_act'][i] = 0
            o_save_dict[uid]['oc_act'][i] = 0
    start_time = time.time()
    num=0
    for uid in uid_list:
        # print(uid)
        o_mid = []
        for list in querry("uid",uid,1):
            print(len(list))
            for message in list:
                # print(message)
                o_mid.append((message['mid'],message['timestamp'],message['time']))
        # print(o_mid)
        for tuple in o_mid:
            mid = tuple[0]
            # print(mid)
            o_save_dict[uid][mid] = dict()
            o_save_dict[uid][mid]['timestamp'] = tuple[1]
            o_save_dict[uid][mid]['date'] = tuple[2]
            for list in querry("root_mid",mid,2):
                o_save_dict[uid][mid]['comment']=len(list)
                for message in list:
                    index = get_queue_index(message['timestamp'])
                    # print(o_save_dict[uid]['oc_act'])
                    o_save_dict[uid]['oc_act'][index] += 1
                    # try:
                    #     o_save_dict[uid][mid]['comment'] += 1
                    # except:
                    #     o_save_dict[uid][mid]['comment'] = 1

            for list in querry("root_mid",mid,3):
                # print(len(list))
                o_save_dict[uid][mid]['retweet']=len(list)
                for message in list:
                    index = get_queue_index(message['timestamp'])
                    o_save_dict[uid]['or_act'][index] += 1

        oc_index_l = o_save_dict[uid]['oc_act'].values()
        max_oc_index = max(oc_index_l)
        oc_activite_time_num = 0
        active_act_num = 0
        for i in oc_index_l:
            if i>int(max_oc_index/2)+1 and i>5:
                oc_activite_time_num += 1
                active_act_num += i
        try:
            oc_ev_av_num = int(active_act_num/oc_activite_time_num)
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
        if num%1000 == 0:
            print(time.time()-start_time)

    db = pymysql.connect(
        host='219.224.134.214',
        port=3306,
        user='root',
        passwd='mysql3306',
        db='PoliticalInfiltration',
        charset='utf8'
    )
    cursor = db.cursor()
    with open('uid.txt','w',encoding='utf8') as wf:
        for uid in o_save_dict.keys():
            wf.write(uid+'\n')


    for uid in o_save_dict.keys():
        # print(uid)
        for mid in o_save_dict[uid].keys():
            if mid != 'or_act' and mid!= 'oc_act':
                # print(mid)
                data = []
                # print(o_save_dict[uid][mid])
                value = (uid,mid,int(o_save_dict[uid][mid]['retweet']),
                         int(o_save_dict[uid][mid]['comment']),int(o_save_dict[uid][mid]['timestamp']),
                         int(o_save_dict[uid]['or_act']['or_activite_time_num']),int(o_save_dict[uid]['or_act']['or_ac_av_num']),
                         int(o_save_dict[uid]['oc_act']['oc_activite_time_num']),int(o_save_dict[uid]['oc_act']['oc_ac_av_num']), o_save_dict[uid][mid]['date'])

                data.append(value)
                sql = "insert into Influence(uid, mid,retweeted,comment,timestamp,original_retweeted_time_num,original_retweeted_average_num," \
                      "original_comment_time_num,original_comment_average_num,date) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s )"
                print(data)
                cursor.executemany(sql, data)
    db.commit()




