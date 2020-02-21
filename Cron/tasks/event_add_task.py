import sys
sys.path.append('../../')
from Config.db_utils import pi_cur, conn
from Cron.event_cal.data_utils import get_edic_add
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


# 对新添加的事件进行计算
def event_add():
    # 获取新添加的事件
    eid_dic = get_edic_add()

    # 分事件进行计算
    print("需要计算事件 {} 个。".format(len(eid_dic)))
    for e_item in eid_dic:
        e_id = e_item['e_id']
        e_name = e_item['event_name']
        start_date = e_item['begin_date']
        end_date = e_item['end_date']

        # 更新为“计算中”
        update_cal_status(e_id, 1)

        # 事件计算
        event_cal_main(e_item, 0, start_date, end_date)

        # 更新为“计算完成”
        update_cal_status(e_id, 2)

        # 更新为“监测中”
        update_monitor_status(e_id, 1)

        print("事件 %s 已添加成功，并计算完成。" % e_name)


if __name__ == '__main__':
    event_add()
