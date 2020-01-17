# -*- coding: utf-8 -*-
import sys
import os
import time
import datetime
from elasticsearch.helpers import scan
from collections import defaultdict
from Mainevent.models import *

sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'

from Config.db_utils import es, pi_cur, conn

cursor = pi_cur()


# 通过信息库里的仍在监听中的敏感微博mid_list，查询流数据，获取当日一跳转发及评论该敏感的流微博信息，
# 返回数据格式{mid1:[{},{}],mid2:[{},{}]}，优先选用search方法，但是采用search方法需要设置es数据库对应索引size
def get_items_from_midList_scan(mid_list):
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
                                    "root_mid": mid_list
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
        mid = item['_source']["root_mid"]
        data_dict[mid].append(item['_source'])

    return data_dict


# search方法需要对es数据库的size进行设定
# curl -XPUT 219.224.134.214:9211/index/_settings -d '{ "index.max_result_window" :"200000000"}' index为需要设定索引名
def get_items_from_midList(mid_list):
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
                                    "root_mid": mid_list
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

    r = es.search(index="weibo_all", body=query_body)["hits"]["hits"]
    for item in r:
        mid = item['_source']["root_mid"]
        data_dict[mid].append(item['_source'])

    return data_dict


# 增加index_name参数的scan方法
def get_items_from_midList_scan1(mid_list, index_name):
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
                                    "root_mid": mid_list
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
        mid = item['_source']["root_mid"]
        data_dict[mid].append(item['_source'])

    return data_dict


# 增加index_name参数的scan方法
def get_items_from_midList1(mid_list, index_name):
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
                                    "root_mid": mid_list
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
        mid = item['_source']["root_mid"]
        data_dict[mid].append(item['_source'])

    return data_dict


# 每天定时从信息库获取仍在监听中的敏感微博列表mid_list；
# 返回两个list，一个原创微博mid_list,一个非原创微博mid_list，非原创微博mid和root_mid的对应关系的字典
def get_mid_list():
    original_mid_dict_list = Information.objects.filter(status=1, message_type=1).values_list("mid", "root_mid")
    non_original_mid_dict_list = Information.objects.filter(status=1, message_type__in=[2, 3]).values_list("mid",
                                                                                                           "root_mid")
    original_mid_list = list(dict(list(original_mid_dict_list)).keys())
    non_original_mid_root_mid_dict = dict(list(non_original_mid_dict_list))
    non_original_mid_list = list(set(list(non_original_mid_root_mid_dict.values())))

    return original_mid_list, non_original_mid_list, non_original_mid_root_mid_dict


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
