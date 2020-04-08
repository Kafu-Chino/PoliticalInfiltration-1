import sys
sys.path.append('../../')

import math

from Config.time_utils import *
from Config.db_utils import es, pi_cur, conn
from Cron.information_cal.data_utils import get_mid_dic_caled
from Cron.information_cal.information_cal_main import information_cal_batch

# 对库中已有计算好的信息进行计算，在bash里定义每日凌晨运行
def information_daily(date):
    # 定时间范围为当前计算日期前一天日期（当天凌晨更新计算前一天的数据）
    end_date = ts2date(int(date2ts(date)) - 86400)
    start_date = end_date

    # 获取未计算的信息
    mid_dic = get_mid_dic_caled()
    batch_num = 10000
    batch_all = math.ceil(len(mid_dic) / batch_num)

    # 批次输入进行计算（如有需要可多进程或分布式）
    print("需要计算信息 {} 条。".format(len(mid_dic)))
    for batch_epoch in range(batch_all):
        mid_dic_batch = mid_dic[batch_epoch * batch_num: (batch_epoch + 1) * batch_num]
        print("信息{}至{}， 共{}".format(batch_epoch * batch_num, (batch_epoch + 1) * batch_num, len(mid_dic)))

        # 计算
        information_cal_batch(mid_dic_batch, start_date, end_date)

        print("该批次计算完成。")


if __name__ == '__main__':
    # date = today()
    date = '2019-08-25'
    information_daily(date)