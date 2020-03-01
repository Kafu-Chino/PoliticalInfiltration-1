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