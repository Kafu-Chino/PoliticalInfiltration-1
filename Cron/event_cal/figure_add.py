import sys
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

def insert_uid(uid_list,e_id):
    uids = ''
    for uid in uid_list:
        uids += uid + ','
    cusor = pi_cur()
    sql = "select figure_id from Event_figure where figure_id in (%s) and event_id='%s'" %(uids[:-1],e_id)
    cusor.execute(sql)
    results = cusor.fetchall()
    id_list = [item['figure_id'] for item in results]
    insert = list(set(uid_list).difference(set(id_list)))
    val = []
    for uid in insert:
        val.append((uid,e_id))
    insert_sql = 'insert into Event_figure(figure_id,event_id) values (%s,%s)'
    try:
        cusor.executemany(insert_sql, val)
        # 获取所有记录列表
        conn.commit()
    except:
        print('错误')
        conn.rollback()
def save_figure(save_dict):
    cusor = pi_cur()
    val = []
    for uid in save_dict:
        val.append((uid,uid,save_dict[uid]))
    sql = "INSERT INTO Figure(f_id,uid,identitystatus,computestatus,monitorstatus) VALUE(%s,%s,%s,0,1) ON DUPLICATE KEY UPDATE " \
          "uid=values(uid),f_id=values(f_id),identitystatus=values(identitystatus)"
    # try:
    cusor.executemany(sql,val)
    # 获取所有记录列表
    conn.commit()
    # except:
    #     print('错误')
    #     conn.rollback()



def figure_add(uid_dict,e_id):
    uid_list = list(set([item['uid'] for item in uid_dict.values()]))
    insert_uid(uid_list,e_id)
    eid_uid = get_event(uid_list)
    total_dict = {}
    for uid in uid_list:
        total_dict[uid] = 0
    for item in eid_uid:
        total_dict[item['figure_id']] += 1
    save_dict = {}
    for uid in uid_list:
        if total_dict[uid]>2:
            save_dict[uid] = 1
        else:
            save_dict[uid] = 0
    save_figure(save_dict)


if __name__ == '__main__':
    uid_dict = {
        '1':{
            'uid':'1'
        }
    }
    e_id = 'xianggang_1582357500'
    figure_add(uid_dict,e_id)

