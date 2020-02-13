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
from user_political import political_classify
from user_influence_total import influence_total



# 批量计算用户
def profile_cal_uidlist(uidlist):
    data = get_uidlist_data(uidlist)
    for date in data:
        print(date)
        if date != '2019-08-12':
            continue
        date_data = data[date]
        word_dict, text_list, text_dict = get_processed_data(date_data, date)

        # 地域特征（文娟）
        # result_position = get_user_activity_aggs(data)

        # 活动特征（文娟）
        # result_msg_type = get_msg_type_aggs(data)

        # 情绪特征（中方）
        # cal_user_emotion(text_dict, data)

        # 影响力特征（英汉）
        influence_total(date,uidlist,word_dict,date_data)

        # 社交特征（梦丽）
        get_user_social(date_data,date)

        #每星期计算一次
        dayOfWeek = datetime.datetime.strptime(date, "%Y-%m-%d").weekday()
        if  dayOfWeek == 2:
            # 话题和领域特征
            thedate = time.strptime(date, "%Y-%m-%d")
            thatday = thedate - datetime.timedelta(days=7)
            topic_domain_cal(uidlist,thedate,thatday)

            # 偏好特征（梦丽）
            get_user_keywords(text_list, word_dict, date, 5)

            #政治倾向（中方）
            # political_classify(uidlist,thedate,thatday)



def main():
    uidlist = get_uid_list()
    batch_num = 1000
    batch_all = math.ceil(len(uidlist) / batch_num)
    for batch_epoch in range(batch_all):
        uidlist_batch = uidlist[batch_epoch * batch_num: (batch_epoch + 1) * batch_num]
        print("用户{}至{}， 共{}".format(batch_epoch * batch_num, (batch_epoch + 1) * batch_num, len(uidlist)))

        profile_cal_uidlist(uidlist_batch)

        # break


if __name__ == '__main__':
    main()



