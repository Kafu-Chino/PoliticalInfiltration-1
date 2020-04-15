import sys
import datetime
sys.path.append('../../')
from Config.db_utils import es,conn,pi_cur

def get_event(uid_list):
    uids = ''
    for uid in uid_list:
        uids += uid + ','
    cusor = pi_cur()
    sql = 'select figure_id,event_id from Event_figure where figure_id in (%s)' %uids[:-1]
    cusor.execute(sql)
    results = cusor.fetchall()
    return results

def get_info(uid_list):
    if len(uid_list)==0:
        return []
    uids = ''
    for uid in uid_list:
        uids += uid + ','
    cusor = pi_cur()
    sql = 'select uid,mid from Information where uid in (%s)' %uids[:-1]
    cusor.execute(sql)
    results = cusor.fetchall()
    return results

def insert_uid(uid_list,e_id):
    uids = ''
    if len(uid_list)==0:
        return 0
    for uid in uid_list:
        uids += uid + ','
    cusor = pi_cur()
    sql = "select figure_id from Event_figure where figure_id in (%s) and event_id='%s'" %(uids[:-1],e_id)
    cusor.execute(sql)
    results = cusor.fetchall()
    # print(results)
    id_list = [item['figure_id'] for item in results]
    # print(id_list)
    insert = list(set(uid_list).difference(set(id_list)))
    # print(insert)
    val = []
    for uid in insert:
        val.append((uid,e_id))
    insert_sql = 'insert into Event_figure(figure_id,event_id) values (%s,%s)'
    try:
        # print(val)
        cusor.executemany(insert_sql, val)
        # 获取所有记录列表
        conn.commit()
    except:
        print('错误')
        conn.rollback()
def save_figure(save_dict):
    cursor = pi_cur()
    val = []
    date = str(datetime.date.today())
    for uid in save_dict:
        cursor.execute('select count(*) from Event_figure where figure_id = %s', uid)
        # print(cursor.fetchone())
        event_count = cursor.fetchone()['count(*)']
        cursor.execute('select count(*) from Information where uid = %s', uid)
        info_count = cursor.fetchone()['count(*)']
        val.append((uid, uid, save_dict[uid], info_count, event_count,date))

    sql = "INSERT INTO Figure(f_id,uid,identitystatus,info_count,event_count,into_date,computestatus,monitorstatus) VALUE(%s,%s,%s,%s,%s,%s,0,1) ON DUPLICATE KEY UPDATE " \
          "uid=values(uid),f_id=values(f_id),identitystatus=values(identitystatus),info_count=values(info_count),event_count=values(event_count),into_date=values(into_date)"
    # try:
    cursor.executemany(sql,val)
    # 获取所有记录列表
    conn.commit()
    # except:
    #     print('错误')
    #     conn.rollback()



def figure_add(uid_dict,e_id):
    uid_list = list(set([item['uid'] for item in uid_dict.values()]))
    insert_uid(uid_list,e_id)
    # eid_uid = get_event(uid_list)
    uid_mid = get_info(uid_list)
    total_dict = {}
    for uid in uid_list:
        total_dict[uid] = 0
    for item in uid_mid:
        total_dict[item['uid']] += 1
    save_dict = {}
    for uid in uid_list:
        if total_dict[uid]>3:
            save_dict[uid] = 1
        else:
            save_dict[uid] = 0
    save_figure(save_dict)


if __name__ == '__main__':
    uid_dict = {
        '2':{
            'uid':'2'
        }
    }
    e_id = 'xianggangshijian_1581919160'
    figure_add(uid_dict,e_id)

