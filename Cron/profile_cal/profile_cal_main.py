#### 在这里导入数据函数和计算函数，写主函数进行计算
#### 可以根据需求，在profile_cal_uidlist和main函数里加入多进程计算或分布式计算，现在单进程顺序操作即可
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


def profile_cal_uidlist(uidlist):
    data = get_items_from_uidList_scan(uidlist)
    result_position = get_user_activity_aggs(data)
    result_msg_type = get_msg_type_aggs(data)
    sql_insert_many(cursor, "UserBehavior", "ub_id", result_msg_type)
    sql_insert_many(cursor, "UserActivity", "ua_id", result_position)


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

