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
    #cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    time1 = time.time()
    info_list = sql_select(cursor, "Figure", field_name="*")
    time2 = time.time()
    print("mysql遍历花费：",time2-time1)
    #print(info_list)
    user_sc={}
    thedate = datetime.date.today()
    #info_all_dict = defaultdict(list)
    info_dict=defaultdict(list)
    for k,v in data_dict.items():
        for item in v:
            #print(item)
            if item["message_type"]==2 or item["message_type"]==3:
                #print("项",item)
                #info_dict[k].append({"source":item["root_uid"],"source_name":" ","target":k,"target_name":" ","message_type":item["message_type"]})
                for info in info_list:
                    if info["uid"] == item["root_uid"]:
                        #print("用户",info["uid"])
                        if info["uid"]==k:
                            info_dict[k].append({"source":item["root_uid"],"source_name":info["nick_name"],"target":k,"target_name":info["nick_name"],"message_type":item["message_type"]})
                        else:
                            info_dict[k].append({"source":item["root_uid"],"source_name":info["nick_name"],"target":k,"target_name":k,"message_type":item["message_type"]})
                        #info_dict[k]["source_name"] = info["nick_name"]
                    else:
                        if info["uid"]==k: 
                            info_dict[k].append({"source":item["root_uid"],"source_name":item["root_uid"],"target":k,"target_name":info["nick_name"],"message_type":item["message_type"]})
                        else:
                            info_dict[k].append({"source":item["root_uid"],"source_name":item["root_uid"],"target":k,"target_name":k,"message_type":item["message_type"]})
        #print(info_dict)
    time3 = time.time()
    print("获取social花费：",time3-time2)
    if len(info_dict):
        for i,v in info_dict.items():
            for num in v:
                user_sc["%s_%s_%s" % (num["target"], num["source"],str(int(time.time())))]={"uid": num["target"],
                                                                                                      "timestamp": int(time.time()),
                                                                                                      "target":num["target"],
                                                                                                      "target_name":num["target_name"],
                                                                                                      "source":num["source"],
                                                                                                      "source_name":num["source_name"],
                                                                                                      "message_type":num["message_type"],
                                                                                                      "store_date":thedate}
        sql_insert_many(cursor, "UserSocialContact", "uc_id", user_sc)
        time4 = time.time()
        print("插入social花费：",time4-time3)
    else:
        print("没有转发或评论数据")



