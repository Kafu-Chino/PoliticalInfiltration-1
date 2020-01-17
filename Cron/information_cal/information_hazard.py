# -*- coding: utf-8 -*-
import time
import datetime
from Mainevent.models import *
from django.db.models import Sum
from Informationspread.models import *


# 计算原创敏感微博的危害指数，参数：计数阈值；
# 输入数据格式为{mid1:[{},{}],mid2:[{},{}]},返回格式{timestamp_mid:{},timestamp_mid:{}}
def get_information_hazard_original(data_dict, count_threshold):
    end_time = int(time.time())
    start_time = end_time - 24 * 60 * 60 * 30
    information_hazard_dict = {}
    for mid in data_dict:
        spread_count = len(data_dict[mid])
        count_s = Informationspread.objects.filter(mid=mid, timestamp__gte=start_time,
                                                   timestamp__lt=end_time).aggregate(spread_count_s=Sum("spread_count"))
        spread_count_s = count_s["spread_count_s"] if count_s["spread_count_s"] else 0
        hazard_index = (spread_count + spread_count_s) / count_threshold
        information_hazard_dict["%s_%s" % (str(end_time), mid)] = {"mid": mid,
                                                                   "root_mid": "",
                                                                   "spread_count": spread_count,
                                                                   "timestamp": end_time,
                                                                   "hazard_index": hazard_index,
                                                                   "store_date": datetime.date.today()}
        Information.objects.filter(mid=mid).update(hazard_index=hazard_index)
    return information_hazard_dict


# 计算非原创敏感微博的危害指数，参数：衰减阈值、计数阈值；
# 输入数据格式为{mid1:[{},{}],mid2:[{},{}]},返回格式{timestamp_mid_root_mid:{},timestamp_mid_root_mid:{}}
def get_information_hazard_non_original(data_dict, count_threshold, reduce_threshold, non_original_mid_root_mid_dict):
    end_time = int(time.time())
    start_time = end_time - 24 * 60 * 60 * 30
    information_hazard_dict = {}
    for root_mid in data_dict:
        spread_count = len(data_dict[root_mid])
        for k, v in non_original_mid_root_mid_dict.items():
            if v == root_mid:
                count_s = Informationspread.objects.filter(mid=k, timestamp__gte=start_time,
                                                           timestamp__lt=end_time).aggregate(
                    spread_count_s=Sum("spread_count"))
                spread_count_s = count_s["spread_count_s"] if count_s["spread_count_s"] else 0
                hazard_index = (spread_count + spread_count_s) * reduce_threshold / count_threshold
                information_hazard_dict["%s_%s_%s" % (str(end_time), k, v)] = {"mid": k,
                                                                               "root_mid": v,
                                                                               "spread_count": spread_count,
                                                                               "timestamp": end_time,
                                                                               "hazard_index": hazard_index,
                                                                               "store_date": datetime.date.today()}
                Information.objects.filter(mid=k).update(hazard_index=hazard_index)
    return information_hazard_dict
