import sys
sys.path.append("../../")
import time
import datetime
from Config.db_utils import ees,conn,pi_cur


def stop_monite():
    cursor = conn.cursor()
    sql = 'select uid from Figure where monitorstatus=1'
    cursor.execute(sql)
    results = cursor.fetchall()
    uid_list = [item['uid'] for item in results]
    if len(uid_list)!=0:
        uids = ''
        for uid in uid_list:
            uids+=uid+','
        day_timestamp = int(time.mktime(datetime.date.today().timetuple()))-86400*100
        sql = "select uid from Information where  uid in (%s) and timestamp>%s "%(uids[:-1],day_timestamp)
        cursor.execute(sql)
        results = cursor.fetchall()
        update_uid = list(set(uid_list).difference(set([item['uid'] for item in results])))
        if len(update_uid)!=0:
            uids = ''
            for uid in update_uid:
                uids += uid + ','
            sql = 'UPDATE Figure SET monitorstatus = 0 WHERE uid in (%s)'%uids[:-1]
            cursor.execute(sql)
            conn.commit()
def start_monite():
    cursor = conn.cursor()
    sql = 'select uid from Figure where monitorstatus=0'
    cursor.execute(sql)
    results = cursor.fetchall()
    uid_list = [item['uid'] for item in results]
    if len(uid_list)!=0:
        uids = ''
        for uid in uid_list:
            uids += uid + ','
        day_timestamp = int(time.mktime(datetime.date.today().timetuple())) - 86400 * 3
        sql = "select uid from Information where  uid in (%s) and timestamp>%s " % (uids[:-1], day_timestamp)
        cursor.execute(sql)
        results = cursor.fetchall()
        update_uid = list(set([item['uid'] for item in results]))
        if len(update_uid)!=0:
            uids = ''
            for uid in update_uid:
                uids += uid + ','
            # print(uids)
            sql = 'UPDATE Figure SET monitorstatus = 1 WHERE uid in (%s)'%uids[:-1]
            cursor.execute(sql)
            conn.commit()

if __name__ == '__main__':
    stop_monite()
    start_monite()



