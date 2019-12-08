# coding = utf - 8
import sys
import os
import time
from elasticsearch.helpers import scan
from collections import defaultdict

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


def get_user_profile_from_uidList(uid_list):
    user_profile_dict = {}
    query_body = {
        "query": {
            'bool': {
                'should': [
                    {"terms": {
                        "uid": uid_list
                    }
                    }
                ]
            }
        }
    }
    r = scan(es, index="weibo_user", query=query_body)
    for item in r:
        uid = item['_source']["uid"]
        del item['_source']['photo_url']
        sex = item['_source']['sex']
        if sex == 2:
            item['_source']['sex'] = 0
        user_birth = item['_source']['user_birth']
        if len(user_birth) == 0:
            item['_source']['user_birth'] = time.strftime("%Y-%m-%d", time.localtime(1539265824))
        item['_source']['create_at'] = time.time()
        # item['_source']['create_at'] = time.mktime(
        #     time.strptime(item['_source'].pop('create_at'), '%Y-%m-%d'))
        user_profile_dict[uid] = item['_source']
    # print(user_profile_dict)
    return user_profile_dict


def sql_select(cursor, table_name, field_name):
    pass


def sql_insert(cursor, table_name, data_dict):
    columns = []
    params = []
    columns.append("f_id")
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
    print(sql)
    n = cursor.executemany(sql, params)
    m = len(params)
    if n == m:
        print("insert %d success" % m)
        conn.commit()
    else:
        print("failed")
    # {"uid": "3185146342",
    #  "sex": 2,
    #  "nick_name": "屮艸芔茻侑",
    #  "user_location": "广东 茂名",
    #  "user_birth": "2000-10-10",
    #  "create_at": "2013-02-10",
    #  "fansnum": 248,
    #  "friendsnum": 388,
    #  "statusnum": 227,
    #  "description": "我爱我的祖国中国"}


def get_items_from_uidList_new(uid_list):
    # end_time = int(time.mktime(datetime.date.today().timetuple()))
    end_time = 1565658944
    # start_time = end_time - 24 * 60 * 60
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
    # end_time = int(time.mktime(datetime.date.today().timetuple()))
    end_time = 1565658944
    # start_time = end_time - 24 * 60 * 60
    start_time = end_time - 24 * 60 * 60
    data_dict = defaultdict(list)
    query_body = {
        "query": {
            'bool': {
                'should': [
                    {"terms": {
                        "uid": uid_list
                    }
                    }
                ]
            }
        }
    }
    # query_body = {
    #     "query": {
    #         "bool": {
    #             "must": [
    #                 {"range": {"timestamp": {"gte": str(start_time), "lt": str(end_time)}}},
    #                 {
    #                     "bool": {
    #                         "should": [
    #                             {"terms": {
    #                                 "uid": uid_list
    #                             }
    #                             }
    #                         ]
    #                     }
    #                 }
    #             ]
    #         }
    #     }
    # }

    r = scan(es, index="weibo_all", query=query_body)
    for item in r:
        uid = item['_source']["uid"]
        data_dict[uid].append(item['_source'])
    # print(data_dict)
    return data_dict


if __name__ == '__main__':
    with open("user_list_union_sus.txt", "r", encoding="utf-8") as f:
        uid_list = [line.strip("\n") for line in f.readlines()]
    data_dict = get_items_from_uidList(uid_list)
    len1 = 0
    for k in data_dict:
        len1 += len(data_dict[k])
    print(len1)
    data_dict_new = get_items_from_uidList_new(uid_list)
    len2 = 0
    for k in data_dict_new:
        len2 += len(data_dict_new[k])
    print(len2)
    # sql_insert(cursor, "Figure", data_dict)
