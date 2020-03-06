### 在这里将get_aggs函数进行拆分，这里只放活动信息统计的部分，该文件不会直接执行，会在profile_cal_main.py里统一调用进行计算。

### 标记好这个统计函数的输入与输出，以便于代码查看
import sys
sys.path.append("../../")

import time
import datetime
from pandas import DataFrame
from Mainevent.models import *
from Cron.profile_cal.data_get_utils import sql_insert_many
from Config.db_utils import es, pi_cur, conn

cursor = pi_cur()
# 获取单个用户的活动特征，输入数据格式为{uid1:[{},{}],uid2:[{},{}]},返回格式{timestamp_uid1:{},timestamp_uid2:{}}
def get_msg_type_aggs(data_dict,date):
    tb = date + " 00:00:00"
    ta = time.strptime(tb, "%Y-%m-%d %H:%M:%S")
    ts = int(time.mktime(ta))
    te = date + " 23:59:59"
    ta = time.strptime(te, "%Y-%m-%d %H:%M:%S")
    te = int(time.mktime(ta))
    user_behavior_dict = {}
    for uid in data_dict:
        #sql = 'select * from Information where uid = %s and ' % uid
        #cursor.execute(sql)
        #cursor.fetchall()
        mid_dict_list = data_dict[uid]
        df = DataFrame(mid_dict_list)
        behavior_dict = get_msg_aggs(df)
        sensitivenum = Information.objects.filter(uid=uid, timestamp__gte=ts, timestamp__lt=te).count()
        behavior_dict["sensitivenum"] = sensitivenum
        behavior_dict["timestamp"] = ts
        behavior_dict["uid"] = uid
        behavior_dict["store_date"] = date
        #print(behavior_dict)
        user_behavior_dict["%s_%s" % (str(ts), uid)] = behavior_dict
    sql_insert_many(cursor, "UserBehavior", "ub_id", user_behavior_dict)

    #return user_behavior_dict


# 获取单个用户的活动特征，输入数据为pandas的df
def get_msg_aggs(df):
    behavior_dict = {}
    res_dict = df.groupby(df["message_type"]).size().to_dict()
    for k, v in res_dict.items():
        if k == 1:
            behavior_dict["originalnum"] = v
        elif k == 2:
            behavior_dict["commentnum"] = v
        elif k == 3:
            behavior_dict["retweetnum"] = v
    if len(behavior_dict) != 3:
        for k in ["originalnum", "commentnum", "retweetnum"]:
            if k not in behavior_dict:
                behavior_dict[k] = 0
    return behavior_dict
