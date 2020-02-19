#-*-coding=utf-8-*-
import sys
import os
import time
import datetime
from collections import defaultdict
from data_get_utils import sql_select,sql_insert_many
from Config.db_utils import es
from elasticsearch.helpers import scan
#cursor = pi_cur()


#计算用户上下游关系
#输入直接得到微博全字段信息
def get_user_social(uidlist,date):
    #cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    time1 = time.time()
    data_list = []
    user_list=[]
    comment_target=[]
    comment_source = []
    retweet_target = []
    retweet_source = []
    #info_list = sql_select(cursor, "Figure", field_name="*")
    query_body = {
        "query": {
            "bool": {
                        "should": [
                            {"terms": {
                                "message_type": [2,3]
                                }
                                }
                            ]
                        }
        }
    }

    r = scan(es, index="weibo_all", query=query_body)
    for item in r:
        user_list.append(item['_source']["uid"])
        user_list.append(item['_source']["root_uid"])
        data_list.append({'uid':item['_source']["uid"],'root_uid':item['_source']["root_uid"],'message_type':item['_source']["message_type"]})
    #user_list.append(uidlist)
    #user_list = list(set(user_list))
    query_body1 = {
        "query": {
            "bool": {
                        "should": [
                            {"terms": {
                                "u_id": user_list
                                }
                                }
                            ]
                        }
        },
        #"size": 2000000
        "size": 10000
    }

    r1 = es.search(index="weibo_user_big", body=query_body1)["hits"]["hits"]
    name_dict = {}
    for item in r1:
        name_dict[item['_source']["u_id"]]=item['_source']["name"]

    #time2 = time.time()
    #print("mysql遍历花费：",time2-time1)
    #print(info_list)
    user_sc={}
    thedate = datetime.date.today()
    #info_all_dict = defaultdict(list)
    info_dict=defaultdict(list)
    for k in uidlist:
        for data in data_list:
            if data["message_type"]==2:
                if data['uid'] == k:
                    comment_source.append({'uid':data["root_uid"],'nick_name':name_dict[data["root_uid"]]})
                if data['root_uid'] == k:
                    comment_target.append({'uid':data["uid"],'nick_name':name_dict[data["uid"]]})
                #info_dict[k].append({"source":data["root_uid"],"source_name":name_dict[data["root_uid"]],"target":k,"target_name":name_dict[k],"message_type":data["message_type"]})
            if data["message_type"]==3:
                #print(name_dict[k])
                if data['uid'] == k:
                    retweet_source.append({'uid':data["root_uid"],'nick_name':name_dict[data["root_uid"]]})
                if data['root_uid'] == k:
                    retweet_target.append({'uid':data["uid"],'nick_name':name_dict[data["uid"]]})
        info_dict[k].append({"retweet_source":retweet_source,"retweet_target":retweet_target,"comment_target":comment_target,"comment_source":comment_source})
            
        '''
        for item in v:
            #print(item)
            if item["message_type"]==2 or item["message_type"]==3:
                #print("项",item)
                #info_dict[k].append({"source":item["root_uid"],"source_name":" ","target":k,"target_name":" ","message_type":item["message_type"]})
                for info in data:
                    if info["root_uid"] == k:
                        #print("用户",info["uid"])
                        if info["uid"]==k:
                            info_dict[k].append({"source":info["uid"],"source_name":info["nick_name"],"target":k,"target_name":info["nick_name"],"message_type":item["message_type"]})
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
    '''
    td = date + " 00:00:00"
    ta = time.strptime(td, "%Y-%m-%d %H:%M:%S")
    ts = int(time.mktime(ta))
    if len(info_dict):
        for i,v in info_dict.items():
            for num in v:
                json_rt = json.dumps(num["retweet_target"],ensure_ascii=False)
                json_rs =json.dumps(num["retweet_source"],ensure_ascii=False)
                json_ct = json.dumps(num["comment_target"],ensure_ascii=False)
                json_cs = json.dumps(num["comment_source"],ensure_ascii=False)
                user_sc["%s_%s" % (i,str(ts))]={"uid": i,
                                                "timestamp": ts,
                                                "retweet_target":json_rt,
                                                "retweet_source":json_rs,
                                                "comment_target":json_ct,
                                                "comment_target":json_cs,
                                                #"message_type":num["message_type"],
                                                "store_date":date}
        sql_insert_many(cursor, "UserSocialContact", "uc_id", user_sc)
        time4 = time.time()
        print("插入social花费：",time4-time1)
    else:
        print("没有转发或评论数据")



