# coding = utf - 8
import sys
import os
import time
import datetime
import random
from elasticsearch.helpers import scan
from collections import defaultdict
from pandas import DataFrame


sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'

from Config.db_utils import es, pi_cur, conn

cursor = pi_cur()


# sql = ""
# cursor.execute(sql)
# cursor.fetchall()
# cursor.close()
# from elasticsearch import Elasticsearch
# from elasticsearch.helpers import scan
#
# ES_HOST = "219.224.134.214"
# ES_PORT = 9211
#
# es = Elasticsearch("%s:%d" % (ES_HOST, ES_PORT), timeout=1000)

# 通过人物库里的uid_list查询流数据，获取微博信息，返回数据格式{uid1:[{},{}],uid2:[{},{}]}，优先选用search方法
def get_items_from_uidList_scan(uid_list):
    end_time = int(time.mktime(datetime.date.today().timetuple()))
    start_time = end_time - 24 * 60 * 60
    data_dict = defaultdict(list)
    # query_body = {
    #     "query": {
    #         'bool': {
    #             'should': [
    #                 {"terms": {
    #                     "uid": uid_list
    #                 }
    #                 }
    #             ]
    #         }
    #     }
    # }
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {"range": {"timestamp": {"gte": str(start_time), "lt": str(end_time)}}},
                    {
                        "bool": {
                            "should": [
                                {"terms": {
                                    "uid": uid_list
                                }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }

    r = scan(es, index="weibo_all", query=query_body)
    for item in r:
        uid = item['_source']["uid"]
        data_dict[uid].append(item['_source'])
    # print(data_dict)
    return data_dict


def get_items_from_uidList(uid_list):
    end_time = int(time.mktime(datetime.date.today().timetuple()))
    start_time = end_time - 24 * 60 * 60
    data_dict = defaultdict(list)
    # query_body = {
    #     "query": {
    #         'bool': {
    #             'should': [
    #                 {"terms": {
    #                     "uid": uid_list
    #                 }
    #                 }
    #             ]
    #         }
    #     }
    # }
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {"range": {"timestamp": {"gte": str(start_time), "lt": str(end_time)}}},
                    {
                        "bool": {
                            "should": [
                                {"terms": {
                                    "uid": uid_list
                                }
                                }
                            ]
                        }
                    }
                ]
            }
        },
        "size": 200000000
    }

    # r = scan(es, index="weibo_all", query=query_body)
    r = es.search(index="weibo_all", body=query_body)["hits"]["hits"]
    for item in r:
        uid = item['_source']["uid"]
        data_dict[uid].append(item['_source'])
    # print(data_dict)
    return data_dict



# mysql查询操作，返回数据格式为单条记录的字典组成的列表
def sql_select(cursor, table_name, field_name="*"):
    sql = 'select %s from %s' % (field_name, table_name)
    cursor.execute(sql)
    return cursor.fetchall()


# 每天定时从人物库获取uid_list，并通过查询流数据获取用户微博信息
def get_data_dict(cursor, table_name, field_name="*"):
    uid_list = set()
    uids = sql_select(cursor, table_name, field_name)
    for uid_dict in uids:
        uid_list.update(list(uid_dict.values()))
    #return get_items_from_uidList(list(uid_list))
    return uid_list



# 通过获取到的用户微博信息，统计用户地域特征、活动特征，并存入mysql数据库
def get_aggs(data_dict):
    user_activity_dict = {}
    user_behavior_dict = {}
    for uid in data_dict:
        mid_dict_list = data_dict[uid]
        df = DataFrame(mid_dict_list)
        behavior_dict = get_user_behavior_aggs(df)
        behavior_dict["timestamp"] = int(time.time())
        behavior_dict["uid"] = uid
        user_behavior_dict["%s_%s" % (str(behavior_dict["timestamp"]), uid)] = behavior_dict
        activity_dict = get_user_activity_aggs(df)
        for k, v in activity_dict.items():
            user_activity_dict["%s_%s_%s" % (str(int(time.time())), uid, k[1])] = {"uid": uid,
                                                                                   "timestamp": int(time.time()),
                                                                                   "geo": k[0], "send_ip": k[1],
                                                                                   "statusnum": v}
    sql_insert_many(cursor, "UserBehavior", "ub_id", user_behavior_dict)
    sql_insert_many(cursor, "UserActivity", "ua_id", user_activity_dict)


# 获取单个用户的地域特征，输入数据为pandas的df
def get_user_activity_aggs(df):
    # res_dict = df.groupby([df["geo"], df["message_type"]]).size().to_dict()
    res_dict = df.groupby([df["geo"], df["send_ip"]]).size().to_dict()
    return res_dict


# 获取单个用户的活动特征，输入数据为pandas的df
def get_user_behavior_aggs(df):
    behavior_dict = {}
    res_dict = df.groupby(df["message_type"]).size().to_dict()
    for k, v in res_dict.items():
        if k == 1:
            behavior_dict["originalnum"] = v
        elif k == 2:
            behavior_dict["commentnum"] = v
        elif k == 3:
            behavior_dict["retweetnum"] = v
    if len(behavior_dict) != 3:
        for k in ["originalnum", "commentnum", "retweetnum"]:
            if k not in behavior_dict:
                behavior_dict[k] = 0
    return behavior_dict


# 向mysql数据库一次存入多条数据，数据输入为data_dict 格式{id1:{item1},id2:{item2},}
def sql_insert_many(cursor, table_name, primary_key, data_dict):
    columns = []
    params = []
    columns.append(primary_key)
    for item_id in data_dict:
        item = data_dict[item_id]
        param_one = []
        param_one.append(item_id)
        for k, v in item.items():
            if k not in columns:
                columns.append(k)
            param_one.append(v)
        params.append(tuple(param_one))
    columns_sql = ",".join(columns)
    values = []
    for i in range(len(columns)):
        values.append("%s")
    values_sql = ",".join(values)
    sql = 'insert into %s (%s) values (%s)' % (table_name, columns_sql, values_sql)
    # print(sql)
    n = cursor.executemany(sql, params)
    m = len(params)
    if n == m:
        print("insert %d success" % m)
        conn.commit()
    else:
        print("failed")



if __name__ == '__main__':
    # 获取人物库敏感人物列表，查询流数据获取人物微博信息
    figure_data_dict = get_data_dict(cursor, "Figure", "uid")
    # 完成人物微博信息的地域、活动特征统计，存入mysql数据库
    get_aggs(figure_data_dict)
