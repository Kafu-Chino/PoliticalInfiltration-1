# -*- coding: UTF-8 -*-
import sys
sys.path.append('../../../')
sys.path.append('../../')
sys.path.append('../')
sys.path.append('../user/')
from config import *
from time_utils import *
from global_utils import *

from user.user_activity import get_user_weibo_type
from user.cron_user import get_weibo_data_dict
from user_fans_task import user_fans_update

# def get_weibo_data_dict(uid, start_date,end_date):
#     weibo_data_dict = {}
#     #对每一天进行微博数据获取
#     for day in get_datelist_v2(start_date, end_date):
#         #print(day)
#         weibo_data_dict[day] = []
#         index_name = "flow_text_" + str(day)
#         query_body ={"query": {"bool": {"must":[{"term": {"uid": uid}}]}}}
#         sort_dict = {'_uid':{'order':'asc'}}
#         ESIterator1 = ESIterator(0,sort_dict,1000,index_name,"text",query_body,es_weibo)
#         while True:
#             try:
#                 #一千条es数据
#                 es_result = next(ESIterator1)
#                 if len(weibo_data_dict[day]):
#                     weibo_data_dict[day].extend(es_result)
#                 else:
#                     weibo_data_dict[day] = es_result
                   
#             except StopIteration:
#                 #遇到StopIteration就退出循环
#                 break
#     return weibo_data_dict


def daily_user_activity(date):
    date = ts2date(int(date2ts(date)) - DAY)
    print(date)
    iter_result = get_user_generator("user_information", {"query":{"bool":{"must":[{"term":{"progress":2}}]}}}, 100000)
    while True:
        try:
            es_result = next(iter_result)
        except:
            break
        uid_list = []
        for k,v in enumerate(es_result):
            uid_list.append(es_result[k]["_source"]["uid"])

        for uid in uid_list:
            weibo_data_dict = get_weibo_data_dict(uid, date,date)
            get_user_weibo_type(uid,weibo_data_dict,date,date)


if __name__ == '__main__':
    # for date in get_datelist_v2('2019-03-30','2019-04-10'):
    #     daily_user_activity(date)
    theday = today()
    print('Calculating user activity...')
    daily_user_activity(theday)
    print('Updating user fans...')    user_fans_update(theday))