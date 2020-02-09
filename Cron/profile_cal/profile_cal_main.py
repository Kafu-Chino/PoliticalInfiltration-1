#-*-coding=utf-8-*-
#### 在这里导入数据函数和计算函数，写主函数进行计算
#### 可以根据需求，在profile_cal_uidlist和main函数里加入多进程计算或分布式计算，现在单进程顺序操作即可
import os
import sys
import math
import django

sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'
django.setup()

from data_utils import get_uid_list, get_uidlist_data
from data_process_utils import get_processed_data
from user_sentiment import cal_user_emotion

# 批量计算用户
def profile_cal_uidlist(uidlist):
    data = get_uidlist_data(uidlist)

    for date in data:
        if date != '2019-08-12':
            continue
        date_data = data[date]
        word_dict, text_list, text_dict = get_processed_data(date_data, date)

        # 地域特征（文娟）
        # result_position = get_user_activity_aggs(data)

        # 活动特征（文娟）
        # result_msg_type = get_msg_type_aggs(data)

        # 偏好特征（梦丽）
        # get_user_keywords(text_list,word_dict,5)

        # 影响力特征（英汉）


        # 社交特征（梦丽）
        # get_user_social(data)

        # 情绪特征（中方）
        # cal_user_emotion(text_dict, data)


def main():
    uidlist = get_uid_list()
    batch_num = 5
    batch_all = math.ceil(len(uidlist) / batch_num)
    for batch_epoch in range(batch_all):
        uidlist_batch = uidlist[batch_epoch * batch_num: (batch_epoch + 1) * batch_num]
        print("用户{}至{}， 共{}".format(batch_epoch * batch_num, (batch_epoch + 1) * batch_num, len(uidlist)))

        profile_cal_uidlist(uidlist_batch)

        break


if __name__ == '__main__':
    main()
