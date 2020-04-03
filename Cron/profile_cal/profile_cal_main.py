import os
import sys
import time
import math
import django
import datetime

sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'
django.setup()

from Cron.profile_cal.data_utils import get_uid_list, get_uidlist_data
from Cron.profile_cal.data_process_utils import get_processed_data
from Cron.profile_cal.user_sentiment import cal_user_emotion
from Cron.profile_cal.user_social import get_user_social
from Cron.profile_cal.user_topic import topic_domain_cal
from Cron.profile_cal.user_keywords import get_user_keywords
from Cron.profile_cal.user_influence_total import influence_total
from Cron.profile_cal.user_political import get_user_political
from Cron.profile_cal.user_influence_total import influence_total
from Cron.profile_cal.user_position import get_user_activity_aggs
from Cron.profile_cal.user_msg_type import get_msg_type_aggs
from Config.db_utils import es,conn,pi_cur

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
        # end_date = datetime.datetime.today()- datetime.timedelta(days=1)
        # start_date = datetime.datetime.strptime(str(datetime.datetime.today() - datetime.timedelta(days=20))[:10],
        #                                         "%Y-%m-%d")

        end_date = '2019-08-25'
        start_date = '2019-06-01'
        # start_date = datetime.datetime.strptime(str(datetime.datetime.strptime(end_date,"%Y-%m-%d") - datetime.timedelta(days=20))[:10],
        #                                         "%Y-%m-%d")
        date_list = getEveryDay(str(start_date)[:10], str(end_date)[:10])
        # date_list.pop(20)
    else:
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        yesterday = today - oneday
        date_list = [str(yesterday)[:10]]
    print(date_list)
    for date in date_list:
        start_time = time.time()
        index = 'flow_text_'+ date
        if es.indices.exists(index):
            print(index)
            data = get_uidlist_data(uidlist,index)
            date_data = data#[date]
            if len(date_data.keys())!=0:
                word_dict, text_list, text_dict = get_processed_data(date_data, date)
            else:
                word_dict, text_list, text_dict = {},{},{}
            time4 = time.time()
            # 地域特征（文娟）
            get_user_activity_aggs(date_data,date)
            time2=time.time()
            print('地域：',time2-start_time)

            # 活动特征（文娟）
            get_msg_type_aggs(date_data,date)
            time3 = time.time()
            print('活动：', time3 - time2)

            # 情绪特征（中方）
            cal_user_emotion(text_dict,date)
            time4 = time.time()
            print('情绪：', time4 - time3)

            # 影响力特征（英汉）
            influence_total(date,uidlist,word_dict,date_data,index)
            time5 = time.time()
            print('影响：', time5 - time4)
             # 社交特征（梦丽）
            get_user_social(uidlist,date_data,date,n)
            time6 = time.time()
            print('社交：', time6 - time5)
            # #
            #每星期计算一次
            dayOfWeek = datetime.datetime.strptime(date, "%Y-%m-%d").weekday()

            if  dayOfWeek == 1:
                # 话题和领域特征
                print('开始周计算')
                thedate = datetime.datetime.strptime(date, "%Y-%m-%d")
                theday = int(time.mktime(time.strptime(date, "%Y-%m-%d")))
                thatdate = thedate - datetime.timedelta(days=7)
                thatday = theday - 86400*7
                topic_domain_cal(uidlist,thatday,theday,thatdate,thedate)
                time7 = time.time()
                print('领域：', time7 - time6)
                # 偏好特征（梦丽）
                get_user_keywords(text_list, word_dict, date, 5)
                time8 = time.time()
                print('偏好：', time8 - time7)
            #
            #     #政治倾向（中方）
                get_user_political(uidlist,thatday,theday)
                time9 = time.time()
                print('政治倾向：', time9 - time8)
            print('总用时',time.time()-start_time)




def profile_cal_main(n,uidlist):
    batch_num = 5000
    batch_all = math.ceil(len(uidlist) / batch_num)
    for batch_epoch in range(batch_all):
        uidlist_batch = uidlist[batch_epoch * batch_num: (batch_epoch + 1) * batch_num]
        print("用户{}至{}， 共{}".format(batch_epoch * batch_num, (batch_epoch + 1) * batch_num, len(uidlist)))

        profile_cal_uidlist(uidlist_batch,n)

        break


# if __name__ == '__main__':
#     profile_cal_main(0)



