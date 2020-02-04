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


# 通过人物库里的uid_list查询流数据，获取微博信息，返回数据格式{uid1:[{},{}],uid2:[{},{}]}，优先选用search方法
def get_items_from_xg1():
    data_dict = defaultdict(list)
    query_body = {
        "query": {
                "terms": {
                    "message_type": [2,3]
                    }
                
                    
        },
        "size": 10000
        #"size": 10000
    }


    r = es.search(index="weibo_all", body=query_body)["hits"]["hits"]
    for item in r:
        uid = item['_source']["uid"]
        data_dict[uid].append(item['_source'])
        #print(data_dict)
    return data_dict


def get_items_from_xg():
    data_dict = defaultdict(list)
    query_body = {
        "query": {
                "match_all": {}
        },
        "size": 10000
        #"size": 10000
    }


    r = es.search(index="event_ostudent", body=query_body)["hits"]["hits"]
    for item in r:
        uid = item['_source']["uid"]
        data_dict[uid].append(item['_source'])
        #print(data_dict)
    return data_dict


if __name__ == '__main__':
    data_dict=get_items_from_xg1()
    print(data_dict)

