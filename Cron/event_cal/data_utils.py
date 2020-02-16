import sys
sys.path.append("../../")
from Config.db_utils import es, pi_cur, conn


def get_eid():
    cursor = pi_cur()
    sql = 'select eid from Event where status = 1,cal_status=0'
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


# 向mysql数据库一次存入多条数据，数据输入为data_dict 格式{id1:{item1},id2:{item2},}
def sql_insert_many(cursor, table_name, primary_key, data_dict):
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
    sql = 'insert into %s (%s) values (%s)' % (table_name, columns_sql, values_sql)
    # print(sql)
    n = cursor.executemany(sql, params)
    m = len(params)
    if n == m:
        print("insert %d success" % m)
        conn.commit()
    else:
        print("failed")