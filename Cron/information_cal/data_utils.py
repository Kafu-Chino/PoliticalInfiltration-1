from Config.db_utils import es, pi_cur, conn

# 取不为人工添加的可计算信息
def get_mid_dic_all():
    cursor = pi_cur()
    sql = 'select * from Information where add_manully = 0'
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# 取不为人工添加的、已计算完成的、且正在监测的信息
def get_mid_dic_caled():
    cursor = pi_cur()
    sql = 'select * from Information where cal_status = 2 and monitor_status = 1 and add_manully = 0'
    cursor.execute(sql)
    result = cursor.fetchall()

    return result

# 取不为人工添加的、且未计算的信息
def get_mid_dic_notcal():
    cursor = pi_cur()
    sql = 'select * from Information where cal_status = 0 and add_manully = 0'
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# 向mysql数据库一次存入多条数据，数据输入为data_dict 格式{id1:{item1},id2:{item2},}
def sql_insert_many(table_name, primary_key, data_dict):
    cursor = pi_cur()
    columns = []
    params = []
    columns.append(primary_key)
    for item_id in data_dict:
        item = data_dict[item_id]
        param_one = []
        param_one.append(item_id)
        for k, v in item.items():
            if k not in columns:
                columns.append(k)
            param_one.append(v)
        params.append(tuple(param_one))
    columns_sql = ",".join(columns)
    values = []
    for i in range(len(columns)):
        values.append("%s")
    values_sql = ",".join(values)
    sql = 'replace into %s (%s) values (%s)' % (table_name, columns_sql, values_sql)

    if len(params):
        n = cursor.executemany(sql, params)
        m = len(params)
        print("insert {} success, {} failed".format(m, m - n))
        conn.commit()
    else:  
        print('empty data')


def check_monitor_status(mid_dic_batch):
    midlist = [item["mid"] for item in mid_dic_batch]
    midlist_format = ""
    for mid in midlist:
        midlist_format += "'{}',".format(mid)
    midlist_format = midlist_format[:-1]

    cursor = pi_cur()
    sql = "SELECT e.monitor_status, i.i_id FROM `Event` e JOIN Event_information ei ON e.e_id = ei.event_id JOIN Information i ON i.i_id = ei.information_id WHERE i.mid IN ({})".format(midlist_format)
    cursor.execute(sql)
    result = cursor.fetchall()

    check_dic = {}
    for item in result:
        i_id = item["i_id"]
        monitor_status = item["monitor_status"]
        if i_id in check_dic:
            check_dic[i_id].append(monitor_status)
        else:
            check_dic[i_id] = [monitor_status]

    params = []
    for i_id in check_dic:
        if sum(check_dic[i_id]) == 0:
            params.append((0, i_id))
    sql = "UPDATE Information SET monitor_status = %s WHERE i_id = %s"
    n = cursor.executemany(sql, params)
    conn.commit()