#-*-coding=utf-8-*-
import sys
import os
import time
import datetime
from collections import defaultdict
from data_get_utils import sql_select,sql_insert_many
from Config.db_utils import es, pi_cur, conn

cursor = pi_cur()


#计算用户上下游关系
#输入直接得到微博全字段信息
def get_user_social(data_dict):
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    info_list = sql_select(cur, "Figure", field_name="*")
    #info_all_dict = defaultdict(list)
    for k,v in data_dict.items():
        for item in v:
            if item["message_type"]==2 or item["message_type"]==3:
                info_dict["source"] = item["root_uid"]
                info_dict["source_name"] = info_dict["source"]
                info_dict["target"] = k
                info_dict["target_name"] = k
                info_dict["message_type"] = item["message_type"]
                for info in info_list:
                    if info["uid"] == source:
                        source_name = info["nick_name"]
                    if info["uid"]==target: 
                        target_name = info["nick_name"]
                info_dict.append()
        #info_all_dict[k] = info_dict
    for i in len(info_dict):
        user_sc["%s_%s_%s" % (info_dict[i]["target"], info_dict[i]["source"],str(int(time.time())))]={"uid": info_dict[i]["target"],
                                                                                                      "timestamp": int(time.time()),
                                                                                                      "target":info_dict[i]["target"],
                                                                                                      "target_name":info_dict[i]["target_name"],
                                                                                                      "source":info_dict[i]["source"],
                                                                                                      "source_name":info_dict[i]["source_name"],
                                                                                                      "message_type":info_dict[i]["message_type"]}
    sql_insert_many(cursor, "UserSocialContact", "uc_id", user_sc)
