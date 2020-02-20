import os
import sys
import time
import math
import django
import datetime

sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'
django.setup()

from data_utils import get_uid_list, get_uidlist_data
from data_process_utils import get_processed_data
from user_sentiment import cal_user_emotion
from user_social import get_user_social
from user_topic import topic_domain_cal
from user_keywords import get_user_keywords
from user_influence_total import influence_total
from user_political import get_user_political
from user_influence_total import influence_total
from user_position import get_user_activity_aggs
from user_msg_type import get_msg_type_aggs


def getEveryDay(begin_date,end_date):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date,"%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list

# 批量计算用户
def profile_cal_uidlist(uidlist,n):
    if n == 0:
        end_date = datetime.datetime.today()
        start_date = datetime.datetime.strptime(str(datetime.datetime.today() - datetime.timedelta(days=20))[:10],
                                                "%Y-%m-%d")
        date_list = getEveryDay(str(start_date)[:10], str(end_date)[:10])
    else:
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        yesterday = today - oneday
        date_list = [str(yesterday)[:10]]
    for date in date_list:
        index = 'flow_text_'+ date
        data = get_uidlist_data(uidlist,index)
        date_data = data[date]
        word_dict, text_list, text_dict = get_processed_data(date_data, date)

        # 地域特征（文娟）
        # result_position = get_user_activity_aggs(data)

        # 活动特征（文娟）
        # result_msg_type = get_msg_type_aggs(data)

        # 情绪特征（中方）
        # cal_user_emotion(text_dict,date)

        # 影响力特征（英汉）
        # influence_total(date,uidlist,word_dict,date_data)
        #
        # # 社交特征（梦丽）
        get_user_social(date_data,date)
        #
        #每星期计算一次
        dayOfWeek = datetime.datetime.strptime(date, "%Y-%m-%d").weekday()
        # if  dayOfWeek == 0:
        #     # 话题和领域特征
        #     print('开始周计算')
        #     thedate = datetime.datetime.strptime(date, "%Y-%m-%d")
        #     theday = int(time.mktime(time.strptime(date, "%Y-%m-%d")))
        #     thatdate = thedate - datetime.timedelta(days=7)
        #     thatday = theday - 86400*7
        #     topic_domain_cal(uidlist,thatday,theday,thatdate,thedate)
        #
        #     # 偏好特征（梦丽）
        #     get_user_keywords(text_list, word_dict, date, 5)
        #
        #     #政治倾向（中方）
        #     get_user_political(uidlist,thatday,theday)



def profile_cal_main(n):
    if n==0:
        uidlist = get_uid_list(n)
    else:
        uidlist = get_uid_list(n)
    batch_num = 1000
    batch_all = math.ceil(len(uidlist) / batch_num)
    for batch_epoch in range(batch_all):
        uidlist_batch = uidlist[batch_epoch * batch_num: (batch_epoch + 1) * batch_num]
        print("用户{}至{}， 共{}".format(batch_epoch * batch_num, (batch_epoch + 1) * batch_num, len(uidlist)))

        profile_cal_uidlist(uidlist_batch,n)

        # break


if __name__ == '__main__':
    profile_cal_main(1)



