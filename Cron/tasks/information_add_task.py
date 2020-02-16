import sys
sys.path.append('../../')

import math

from Config.time_utils import *
from Config.db_utils import es, pi_cur, conn
from Cron.information_cal.data_utils import get_mid_dic_all, get_mid_dic_notcal
from Cron.information_cal.information_cal_main import information_cal_batch

# 更新信息库计算状态
def update_cal_status(mid_dic, cal_status):
    cursor = pi_cur()
    sql = "UPDATE Information SET cal_status = %s WHERE i_id = %s"

    params = [(cal_status, item["i_id"]) for item in mid_dic]
    n = cursor.executemany(sql, params)
    conn.commit()

# 对新添加的信息进行计算，在bash里定义5分钟一运行
def information_add(date):
    # 定时间范围为当前计算日期前一天日期至前十五天内（当天数据当天晚上统一更新计算）
    end_date = ts2date(int(date2ts(date)) - 86400)
    start_date = ts2date(int(date2ts(date)) - 16 * 86400)

    # 获取未计算的信息
    mid_dic = get_mid_dic_notcal()
    batch_num = 10000
    batch_all = math.ceil(len(mid_dic) / batch_num)

    # 批次输入进行计算（如有需要可多进程或分布式）
    print("需要计算用户 {} 人。".format(len(mid_dic)))
    for batch_epoch in range(batch_all):
        mid_dic_batch = mid_dic[batch_epoch * batch_num: (batch_epoch + 1) * batch_num]
        print("信息{}至{}， 共{}".format(batch_epoch * batch_num, (batch_epoch + 1) * batch_num, len(mid_dic)))

        # 更新为“计算中”
        update_cal_status(mid_dic_batch, 1)
        # 计算
        information_cal_batch(mid_dic_batch, start_date, end_date)
        # 更新为“计算完成”
        update_cal_status(mid_dic_batch, 2)

        print("该批次计算完成。")


if __name__ == '__main__':
    date = today()
    # date = '2019-08-26'
    information_add(date)
