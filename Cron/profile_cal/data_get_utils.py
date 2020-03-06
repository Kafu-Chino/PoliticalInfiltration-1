#-*-coding=utf-8-*-
import sys
import os
import time
import datetime
from elasticsearch.helpers import scan
from collections import defaultdict

sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'

from Config.db_utils import es, pi_cur, conn

cursor = pi_cur()


# 通过人物库里的uid_list查询流数据，获取当日微博信息，返回数据格式{uid1:[{},{}],uid2:[{},{}]}，优先选用search方法
def get_items_from_uidList_scan(uid_list):
    end_time = int(time.mktime(datetime.date.today().timetuple()))
    start_time = end_time - 24 * 60 * 60
    data_dict = defaultdict(list)

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

    return data_dict


# search方法需要对es数据库的size进行设定
# curl -XPUT 219.224.134.214:9211/index/_settings -d '{ "index.max_result_window" :"200000000"}' index为需要设定索引名
def get_items_from_uidList(uid_list):
    end_time = int(time.mktime(datetime.date.today().timetuple()))
    #end_time = 1565658944
    start_time = end_time - 24 * 60 * 60
    data_dict = defaultdict(list)

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
        #"size": 10000
    }

    r = es.search(index="weibo_all", body=query_body)["hits"]["hits"]
    for item in r:
        uid = item['_source']["uid"]
        data_dict[uid].append(item['_source'])

    return data_dict


# 增加index_name参数的scan方法
def get_items_from_uidList_scan1(uid_list, index_name):
    end_time = int(time.mktime(datetime.date.today().timetuple()))
    start_time = end_time - 24 * 60 * 60
    data_dict = defaultdict(list)

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

    r = scan(es, index=index_name, query=query_body)
    for item in r:
        uid = item['_source']["uid"]
        data_dict[uid].append(item['_source'])

    return data_dict


# 增加index_name参数的search方法
def get_items_from_uidList1(uid_list, index_name):
    end_time = int(time.mktime(datetime.date.today().timetuple()))
    start_time = end_time - 24 * 60 * 60
    data_dict = defaultdict(list)

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

    r = es.search(index=index_name, body=query_body)["hits"]["hits"]
    for item in r:
        uid = item['_source']["uid"]
        data_dict[uid].append(item['_source'])

    return data_dict


# mysql查询操作，返回数据格式为单条记录的字典组成的列表
def sql_select(cursor, table_name, field_name="*"):
    sql = 'select %s from %s' % (field_name, table_name)
    cursor.execute(sql)
    return cursor.fetchall()


# 每天定时从人物库获取uid_list，并通过查询流数据获取用户微博信息
def get_data_dict(table_name, field_name="*"):
    cursor = pi_cur()
    uid_list = set()
    uids = sql_select(cursor, table_name, field_name)
    for uid_dict in uids:
        uid_list.update(list(uid_dict.values()))
    return get_items_from_uidList(list(uid_list))


# 每天定时从人物库获取uid_list
def get_uid_list(table_name, field_name="*"):
    cursor = pi_cur()
    uid_list = set()
    uids = sql_select(cursor, table_name, field_name)
    for uid_dict in uids:
        uid_list.update(list(uid_dict.values()))
    return list(uid_list)


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
