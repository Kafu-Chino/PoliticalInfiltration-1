#-*-coding=utf-8-*-
#### 在这里导入数据函数和计算函数，写主函数进行计算
#### 可以根据需求，在profile_cal_uidlist和main函数里加入多进程计算或分布式计算，现在单进程顺序操作即可
import django
import sys
import os

sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'
django.setup()

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

from data_utils import get_uid_list, get_uidlist_data
from data_process_utils import get_processed_data
from user_sentiment import cal_user_emotion


# 批量计算用户
def profile_cal_uidlist(uidlist):
	data = get_items_from_uidList(uidlist)
    result_position = get_user_activity_aggs(data)
    result_msg_type = get_msg_type_aggs(data)
    sql_insert_many(cursor, "UserBehavior", "ub_id", result_msg_type)
    sql_insert_many(cursor, "UserActivity", "ua_id", result_position)
	word_dict,text_list = get_processed_data(data)
	get_user_social(data)
	get_user_keywords(text_list,word_dict,5)
    # 地域特征（文娟）
    # result_position = get_user_activity_aggs(data)

    # 活动特征（文娟）
    # result_msg_type = get_msg_type_aggs(data)

    # 偏好特征（梦丽）


    # 影响力特征（英汉）


    # 社交特征（梦丽）


    # 情绪特征（中方）
    


def main():
    uidlist = get_uid_list()
    batch_num = 1000
    batch_all = math.ceil(len(uidlist) / batch_num)
    for batch_epoch in range(batch_all):
        uidlist_batch = uidlist[batch_epoch * batch_num: (batch_epoch + 1) * batch_num]
        print("用户{}至{}， 共{}".format(batch_epoch * batch_num, (batch_epoch + 1) * batch_num, len(uidlist)))

        profile_cal_uidlist(uidlist_batch)


if __name__ == '__main__':
    main()
