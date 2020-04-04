import sys
sys.path.append("../../")

import os
import time
import datetime
from Cron.profile_cal.data_utils import sql_insert_many1, get_uid_list
from Config.db_utils import es, pi_cur#, es_floww
from Config.time_utils import *
from elasticsearch.helpers import scan

def get_user_social(uidlist, date_data, date,n):
    """
    result_dic格式：
    {
        (source_uid, target_uid): {
            2: 评论数,
            3: 转发数,
        }
    }
    """
    # 上游数据补充查询
    # list_all = set(get_uid_list(n))
    query_body = {
        "query":{
            "bool":{
                "must":[
                    {"terms": {"root_uid": uidlist}}
                ]
            }
        }
    }

    # 本地weibo_all
    start_ts = date2ts(date)
    end_ts = date2ts(date) + 86400
    query_body["query"]["bool"]["must"].append({"range": {"timestamp": {"gte": start_ts, "lt": end_ts}}})
    # es_scan_iter = scan(es, index="weibo_all", query=query_body)
    # append_data = [item["_source"] for item in es_scan_iter]

    # 流数据，部署时注释本地代码，使用该段代码
    es_scan_iter = scan(es, index="flow_text_{}".format(date), query=query_body)#es_flow
    append_data = [item["_source"] for item in es_scan_iter]


    # 上下游数据遍历计数
    result_dic = {}
    date_data_new = []
    for uid in date_data:
        for item in date_data[uid]:
            date_data_new.append(item)
    date_data_new.extend(append_data)
    uidlist_append = []

    mid_set = set([])
    for item in date_data_new:
        mid = item["mid"]
        if mid in mid_set:
            continue
        else:
            mid_set.add(mid)

        uid = item["uid"]
        root_uid = item["root_uid"]
        message_type = item["message_type"]
        key = (root_uid, uid)
        uidlist_append.append(uid)
        if root_uid:
            uidlist_append.append(root_uid)

        if key not in result_dic:
            result_dic[key] = {
                2: 0,
                3: 0
            }

        if message_type == 2:
            result_dic[key][2] += 1
        elif message_type == 3:
            result_dic[key][3] += 1

    # 用户昵称es库查询
    cursor = pi_cur()
    sql = "SELECT uid, nick_name from Figure where uid in ('{}')".format("','".join(uidlist))
    cursor.execute(sql)
    result = cursor.fetchall()
    nick_name_dic = {item["uid"]: item["nick_name"] for item in result}
    
    uidlist_append = list(set(uidlist_append) - set(uidlist))
    query_body = {
        "query":{
            "terms": {
                "u_id": uidlist_append
            }
        }
    }
    es_scan_iter = scan(es, index='weibo_user_big', query=query_body)
    for item in es_scan_iter:
        nick_name_dic[str(item["_source"]["u_id"])] = item["_source"]["name"]

    # 数据存储入社交统计库，只有大库中存在的相关用户的关系才会被存储，只有数量多于2的边才会存储
    insert_dic = {}
    for key in result_dic:
        if key[0] in nick_name_dic and key[1] in nick_name_dic:
            for message_type in result_dic[key]:
                if result_dic[key][message_type] >= 2:
                    uc_id = "{}_{}_{}_{}".format(date2ts(date), key[0], key[1], message_type)
                    insert_dic[uc_id] = {
                        "target": key[1],
                        "target_name": nick_name_dic[key[1]],
                        "source": key[0],
                        "source_name": nick_name_dic[key[0]],
                        "message_type": message_type,
                        "count": result_dic[key][message_type],
                        "timestamp": date2ts(date),
                        "store_date": date,
                    }
    sql_insert_many1("UserSocialContact", "uc_id", insert_dic)

if __name__ == "__main__":
    cursor = pi_cur()
    sql = "SELECT uid, nick_name from Figure where uid in ({})".format(",".join(["1000124571", "1002383394"]))
    cursor.execute(sql)
    result = cursor.fetchall()
    print(result)