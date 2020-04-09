import sys
sys.path.append('../../')
from Config.time_utils import *
from Config.db_utils import pi_cur, conn, get_event_para
from Cron.event_cal.data_utils import get_edic_daily
from Cron.event_cal.event_cal_main import event_cal_main


# 更新事件库计算状态
def update_cal_status(eid, cal_status):
    cursor = pi_cur()
    sql = "UPDATE Event SET cal_status = %s WHERE e_id = %s"

    params = [(cal_status, eid)]
    n = cursor.executemany(sql, params)
    conn.commit()


# 更新事件库监测状态
def update_monitor_status(eid, status):
    cursor = pi_cur()
    sql = "UPDATE Event SET monitor_status = %s WHERE e_id = %s"

    params = [(status, eid)]
    n = cursor.executemany(sql, params)
    conn.commit()


# 更新事件库峰值
def update_count_max(eid, max_num):
    cursor = pi_cur()
    sql = "UPDATE Event SET count_max = %s WHERE e_id = %s"

    params = [(max_num, eid)]
    n = cursor.executemany(sql, params)
    conn.commit()


# 对库中已有计算好的事件进行计算，在bash里定义每日凌晨运行
def event_daily(date):
    # 定时间范围为当前计算日期前一天日期（当天凌晨更新计算前一天的数据）
    end_date = ts2date(int(date2ts(date)) - 86400)
    start_date = end_date

    # 获取监测中，计算已完成的事件信息
    eid_dic = get_edic_daily()

    # 分事件进行计算
    print("需要计算事件 {} 个。".format(len(eid_dic)))
    for e_item in eid_dic:
        e_id = e_item['e_id']
        e_name = e_item['event_name']
        max_num = e_item['count_max']
        try:
            stop_percent = get_event_para(e_id, 'stop_percent')
        except:
            stop_percent = 0.05
            store_event_para(e_id, 'stop_percent')

        # 更新为“计算中”
        update_cal_status(e_id, 1)

        # 事件计算
        new_max_num = event_cal_main(e_item, 1, start_date, end_date)

        if new_max_num > max_num:
            # 更新峰值
            update_count_max(e_id, new_max_num)
        if new_max_num < max_num * stop_percent:
            # 更新为“停止监测”
            update_monitor_status(e_id, 0)

        # 更新为“计算完成”
        update_cal_status(e_id, 2)

        print("事件 %s 已计算完成。" % e_name)


if __name__ == '__main__':
    date = today()
    # date = '2019-08-26'
    event_daily(date)
