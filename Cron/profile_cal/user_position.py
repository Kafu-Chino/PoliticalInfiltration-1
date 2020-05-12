### 在这里将get_aggs函数进行拆分，这里只放地点统计的部分，该文件不会直接执行，会在profile_cal_main.py里统一调用进行计算。

### 标记好这个统计函数的输入与输出，以便于代码查看
import sys
import os,django
sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'
django.setup()
import time
import datetime
from pandas import DataFrame
from Mainevent.models import *
from collections import defaultdict
from Cron.profile_cal.data_utils import sql_insert_many
from Config.db_utils import es, pi_cur, conn
cursor = pi_cur()


# 获取单个用户的地域特征，输入数据格式为{uid1:[{},{}],uid2:[{},{}]},返回格式{timestamp_uid_send_ip1:{},timestamp_uid_send_ip2:{}}
def get_user_activity_aggs(data_dict,date):
    #end_time = int(time.time())
    end_time=datetime.datetime.strptime(date+ " 23:59:59", '%Y-%m-%d %H:%M:%S').timestamp()
    start_time = end_time - 24 * 60 * 60
    user_activity_dict = {}
    ip_dict={}
    for uid in data_dict:
        #geo_ip_dict = defaultdict(set)
        mid_dict_list = data_dict[uid]
        #print(mid_dict_list)
        df = DataFrame(mid_dict_list)
        geo_dict = df.groupby([df["geo"]]).size().to_dict()
        #print(geo_dict)
        #print(uid)
        '''无ip信息，后期补上
        activity_dict = df.groupby([df["geo"], df["send_ip"]]).size().to_dict()
        for k, v in activity_dict.items():
            geo_ip_dict[k[0]].add(k[1][:(k[1].rindex(".") + 1)] + "*")
            '''
        for index,row in df.iterrows():
            ip_dict[row["geo"]] = row["ip"]
            #print(row['geo'])
            #try:
                #ip_dict[row["geo"]] = row["ip"]
            #except:
                #continue
        #print(ip_dict)
        for k in geo_dict:
            #print(k)
            #ips = ",".join(list(geo_ip_dict[k])) #无ip信息 后期补上
            ip = ip_dict[k]
            if ip is None:
                ip="未知"
            #ip = geo_ip_dict[k]
            statusnum = geo_dict[k]
            #print(geo_dict[k])
            sensitivenum = Information.objects.filter(uid=uid, timestamp__gte=start_time,
                                                      timestamp__lt=end_time, geo=k).count()
            user_activity_dict["%s_%s_%s" % (str(end_time), uid, k)] = {"uid": uid,
                                                                        "timestamp": end_time,
                                                                        "geo": k, "send_ip": ip,
                                                                        "statusnum": statusnum,
                                                                        "sensitivenum": sensitivenum,
                                                                        "store_date": date}
    sql_insert_many(cursor, "UserActivity", "ua_id", user_activity_dict)
    
    #return user_activity_dict

'''
if __name__ == '__main__':
    data = {'1744':[{"data":"test","geo":'beijing',"ip":'1135'},{"data":"test","geo":'beijing',"ip":'1135'}]}
    date = '2020-05-05'
    get_user_activity_aggs(data,date)
'''
