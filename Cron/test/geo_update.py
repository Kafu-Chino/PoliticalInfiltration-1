import re
import time
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, bulk

ES_HOST = '219.224.135.12'
ES_PORT = 9211
es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)

import sys
sys.path.append("../../")
from Config.db_utils import pi_cur, conn

with open("国家") as f:
    country_list = f.readlines()
country_list = [line.strip() for line in country_list]
with open("市") as f:
    data = f.readlines()
province_list = []
city_list = []
city_dic = {}
for line in data:
    line = line.strip().split("： ")
    province_list.append(line[0])
    pro_city = line[1].split()
    city_list.extend(pro_city)
    for city in pro_city:
        city_dic[city] = line[0]

re_country = re.compile("|".join(country_list))
re_province = re.compile("|".join(province_list))
re_city = re.compile("|".join(city_list))

def geo_transfer(geo):
    country_find = re_country.findall(geo)
    if len(country_find):
        country = country_find[0]
    else:
        country = "未知"

    province_find = re_province.findall(geo)
    if len(province_find):
        province = province_find[0]
        country = "中国"
    else:
        province = "未知"

    city_find = re_city.findall(geo)
    if len(city_find):
        city = city_find[0]
        country = "中国"
        if province == '未知':
            province = city_dic[city]
        elif province != city_dic[city]:
            city = "未知"
    else:
        city = "未知"

    return "{}&{}&{}".format(country, province, city)

def datetime2ts(date):
    return int(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S')))

def update_weibo_all_geo():
    query_body = {
        "query": {
            "bool": {
                "must_not": {
                    "exists": {
                        "field": "geo_old"
                    }
                }
            }
        }
    }
    # query_body = {
    #     "query":{
    #         "match_all": {}
    #     }
    # }
    # for es_index in ["event_muji", "event_ostudent", "event_rollsroyce", "event_tradewar", "event_uktruck", "event_yuzhang"]:
    for es_index in ["weibo_all"]:
        result = scan(es, index=es_index, query=query_body)
        bulk_list = []
        for index, item in enumerate(result):
            id = item["_id"]
            item = item["_source"]
            if "geo" not in item:
                item["geo"] = "字段缺失"
            geo_new = geo_transfer(item["geo"])

            data = {}
            data['_index'] = es_index
            data['_op_type'] ='update'
            data['_id'] = id
            data['_type'] = es_index
            data['doc'] = {
                "geo_old": item["geo"],
                "geo": geo_new,
                # "timestamp": datetime2ts(item["time"])
            }
            bulk_list.append(data)

            if index % 1000 == 0:
                print(es_index, index)
                bulk(es, bulk_list)
                bulk_list = []

        bulk(es, bulk_list)

def update_mysql_geo():
    cur = conn.cursor()
    sql = "SELECT * from Information, Event_information WHERE Event_information.event_id = 'xianggangshijian_1581919160' and Information.i_id = Event_information.information_id"
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()

    cursor = pi_cur()
    for index, item in enumerate(data):
        geo = item["geo"]
        i_id = item["i_id"]
        geo_new = geo_transfer(geo)
        update_sql = "UPDATE Information SET geo='{}' WHERE i_id='{}'".format(geo_new, i_id)
        cursor.execute(update_sql)
        print(index)
    conn.commit()

if __name__ == "__main__":
    # geo = "河北省邯郸市电信(河北省邯郸市电信)"
    # print(geo_transfer(geo))
    # update_weibo_all_geo()
    update_mysql_geo()