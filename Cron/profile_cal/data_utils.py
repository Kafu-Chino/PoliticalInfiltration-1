import sys
from elasticsearch.helpers import scan

sys.path.append("../../")
from Config.db_utils import es, pi_cur
from Config.time_utils import *

# 每天定时从人物库获取uid_list
def get_uid_list():
    cursor = pi_cur()
    sql = 'select %s from %s' % ("uid", "Figure")
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
