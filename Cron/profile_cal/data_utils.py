import sys
from elasticsearch.helpers import scan

sys.path.append("../../")
from Config.db_utils import es, pi_cur, conn
from Config.time_utils import *

# 每天定时从人物库获取uid_list
def get_uid_list():
    cursor = pi_cur()
    sql = 'SELECT %s from %s order by uid' % ("uid", "Figure")
    cursor.execute(sql)
    result = cursor.fetchall()
    uidlist = [item["uid"] for item in result]
    return uidlist

# 根据uidlist获取数据
def get_uidlist_data(uidlist):#, start_date, end_date
    # start_ts = date2ts(start_date)
    # end_ts = date2ts(end_date)
    query_body = {
        "query": {
            "bool": {
                "must": [
                    # {"range": {"timestamp": {"gte": start_ts, "lt": end_ts}}},
                    {"terms": {"uid": uidlist}}
                ]
            }
        }
    }

    result = scan(es, index="weibo_all", query=query_body)

    data = {}
    for item in result:
        item = item["_source"]
        date = ts2date(item["timestamp"])
        uid = item["uid"]
        if date in data:
            if uid in data[date]:
                data[date][uid].append(item)
            else:
                data[date][uid] = [item]
        else:
            data[date] = {uid: [item]}

    return data

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

    m = len(params)
    if m == 0:
        print("empty data")
        return
    n = cursor.executemany(sql, params)
    if n == m:
        print("insert %d success" % m)
        conn.commit()
    else:
        print("%d success, %d failed" % (n, m - n))