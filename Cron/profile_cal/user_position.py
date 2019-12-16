### 在这里将get_aggs函数进行拆分，这里只放地点统计的部分，该文件不会直接执行，会在profile_cal_main.py里统一调用进行计算。

### 标记好这个统计函数的输入与输出，以便于代码查看


import sys
import os
import time
import datetime
from pandas import DataFrame

sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'


# 获取单个用户的地域特征，输入数据格式为{uid1:[{},{}],uid2:[{},{}]},返回格式{timestamp_uid_send_ip1:{},timestamp_uid_send_ip2:{}}
def get_user_activity_aggs(data_dict):
    user_activity_dict = {}
    for uid in data_dict:
        mid_dict_list = data_dict[uid]
        df = DataFrame(mid_dict_list)
        activity_dict = df.groupby([df["geo"], df["send_ip"]]).size().to_dict()
        for k, v in activity_dict.items():
            user_activity_dict["%s_%s_%s" % (str(int(time.time())), uid, k[1])] = {"uid": uid,
                                                                                   "timestamp": int(time.time()),
                                                                                   "geo": k[0], "send_ip": k[1],
                                                                                   "statusnum": v,
                                                                                   "store_date": datetime.date.today()}
    return user_activity_dict
