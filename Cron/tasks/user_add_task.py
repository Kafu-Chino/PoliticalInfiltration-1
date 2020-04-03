import sys
sys.path.append('../../')
from Config.db_utils import pi_cur, conn
from Cron.profile_cal.profile_cal_main import profile_cal_main
from Cron.profile_cal.data_utils import get_uid_list1

#更新人物计算状态
def update_cal_status(uid_list, computestatus):
    cursor = pi_cur()
    sql = "UPDATE Figure SET computestatus = %s WHERE uid = %s"

    params = [(computestatus, item) for item in uid_list]
    n = cursor.executemany(sql, params)
    conn.commit()

def user_add_cal():
    uid_list = get_uid_list1(0)
    # 更新为计算中
    update_cal_status(uid_list,1)
    #启动计算
    profile_cal_main(0,uid_list)
    #更新计算状态为计算完成
    update_cal_status(uid_list, 2)
    print("新增人物计算完成。" )

if __name__ == '__main__':
    user_add_cal()