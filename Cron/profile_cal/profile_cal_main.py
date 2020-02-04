#### 在这里导入数据函数和计算函数，写主函数进行计算
#### 可以根据需求，在profile_cal_uidlist和main函数里加入多进程计算或分布式计算，现在单进程顺序操作即可
import django
import sys
import os

sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'
django.setup()

import math
from data_utils import get_uid_list, get_uidlist_data
from data_process_utils import get_processed_data
from user_sentiment import cal_user_emotion

# 批量计算用户
def profile_cal_uidlist(uidlist):
    data = get_uidlist_data(uidlist)
    word,text = get_processed_data(data)

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
