#-*-coding=utf-8-*-
#### 在这里导入数据函数和计算函数，写主函数进行计算
#### 可以根据需求，在profile_cal_uidlist和main函数里加入多进程计算或分布式计算，现在单进程顺序操作即可
<<<<<<< Updated upstream
import django
import sys
import os

sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'
django.setup()

import math
from Cron.profile_cal.data_get_utils import *
from Cron.profile_cal.user_position import *
from Cron.profile_cal.user_msg_type import *
from data_expand import get_items_from_xg1
from data_get_utils import get_items_from_uidList, get_data_dict, sql_insert_many
import math
import time,datetime
from collections import defaultdict
from user_position import *
from user_msg_type import *
from user_topic import get_user_topic
from user_domain import get_user_domain
from user_social import get_user_social
from user_keywords import get_user_keywords
from data_process_utils import get_processed_data
from Config.db_utils import es, pi_cur, conn
import json
cursor = pi_cur()
#from topic import topic_tfidf,get_p1

thedate = datetime.date.today()
thatday = thedate - datetime.timedelta(days=7)
#print(thedate,thatday)
def topic_domain_cal(start_date=thatday,end_date=thedate):
    sql = 'select uid,wordcount from WordCount' #where store_date >= %s and store_date <= %s' % (start_date,end_date)
    cursor.execute(sql)
    word_c =defaultdict(dict)
    word = {}
    result = cursor.fetchall()
    #result1 = json.loads(result)
    for i in result:
        item = json.loads(i['wordcount'])
        #print(type(i[wordcount]))
        for k,v in item.items():
            try:
                word_c[i['uid']][k] += v
            except:
                word_c[i['uid']][k] = v
    #print(word_c)
    get_user_topic(word_c)
    get_user_domain(word_c)


def profile_cal_uidlist(uidlist):
	data = get_items_from_uidList(uidlist)
    result_position = get_user_activity_aggs(data)
    result_msg_type = get_msg_type_aggs(data)
    sql_insert_many(cursor, "UserBehavior", "ub_id", result_msg_type)
    sql_insert_many(cursor, "UserActivity", "ua_id", result_position)
	word_dict,text_list = get_processed_data(data)
	get_user_social(data)
	get_user_keywords(text_list,word_dict,5)



def main():
    uidlist = get_uid_list(cursor, "Figure", "uid")
    uidlist_new = []
    n = math.ceil(len(uidlist) / 1000)
    for i in range(n):
        uids = uidlist[i * 1000, (i + 1) * 1000]
        uidlist_new.append(uids)
    for uidlist_sub in uidlist_new:
        profile_cal_uidlist(uidlist_sub)


if __name__ == '__main__':
    main()
#	uid_list=["5241560394","6598780267"]
    time_start = time.time()
    #topic_domain_cal()
    time_e = time.time()
    print("花费：",time_e-time_start)
#	data =  {'5241560394': [{'source': '新浪', 'uid': '5241560394', 'root_uid': '', 'mid': '4404755222396058', 'root_mid': '', 'time': '2019-08-13 09:15:44', 'message_type': 1, 'sentiment': '0', 'text': '#外国人香港机场教训示威者# 看了这个视频我终于知道了什么叫:你永远滋不醒一个张嘴接尿的人http://t.cn/AiHh83xh ', 'geo': '\x08(国外未知未知)', 'net_type': '荣耀20 PRO', 'user_fansnum': 43, 'timestamp': 1565658944.0}], '6598780267': [{'source': '新浪', 'uid': '6598780267', 'root_uid': '', 'mid': '4404757026037564', 'root_mid': '', 'time': '2019-08-13 09:22:54', 'message_type': 1, 'sentiment': '-15', 'text': '#搜狐资讯#《香港机场再遭示威者瘫痪 今日余下航班全部取消》大批示威者今天聚集香港国际机场（联合早报网）海外网8月12日http://t.cn/AiHZDiWp ', 'geo': '中国移动(国外未知未知)', 'net_type': '搜狐资讯', 'user_fansnum': 3, 'timestamp': 1565659374.0}, {'source': '新浪', 'uid': '6598780267', 'root_uid': '', 'mid': '4405455973350546', 'root_mid': '', 'time': '2019-08-15 07:40:16', 'message_type': 1, 'sentiment': '-9', 'text': '#搜狐资讯#《内地记者在香港机场被示威者拘押殴打 被警方 救出》13日晚，环球网记者付国豪在香港机场被示威者非法拘押，遭到非http://t.cn/AiHiTdKD ', 'geo': '中国移动(国外未知未知)', 'net_type': '搜狐资讯', 'user_fansnum': 3, 'timestamp': 1565826016.0}]}
    data = get_items_from_xg1()
    #print(data)
    time_e = time.time()
    print("查数据花费：",time_e-time_start)
    #get_user_social(data)
    #word_dict,text_list = get_processed_data(data)
    #print(word_dict)
    time_e2 = time.time()
    get_user_social(data)
    time_e5 = time.time()
    print("social花费：",time_e5-time_e2)
    #print("处理数据：",time_e2-time_start)
    #get_user_keywords(text_list,word_dict,5)
    '''
    get_user_topic(word_dict)
    time_e3 = time.time()
    print("topic花费：",time_e3-time_e2)
    get_user_domain(word_dict)
    time_e4 = time.time()
    print("domain花费：",time_e4-time_e3)
    get_user_social(data)
    time_e5 = time.time()
    print("social花费：",time_e5-time_e4)
    get_user_keywords(text_list,word_dict,5)
    time_end = time.time()
    print("kw花费：",time_end-time_e5)
    print("time cost:",time_end-time_start,'s')'''

