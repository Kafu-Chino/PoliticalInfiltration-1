# -*- coding: utf-8 -*-
import django
import sys
import os

sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'
django.setup()

import math
from Cron.information_cal.data_get_utils import *
from Cron.information_cal.information_hazard import *
from Config.base import *


def profile_cal_midlist_original(midlist):
    data = get_items_from_midList_scan(midlist)
    print(data)
    result = get_information_hazard_original(data, count_threshold)
    sql_insert_many(cursor, "Informationspread", "is_id", result)


def profile_cal_midlist_non_original(midlist, non_original_mid_root_mid_dict):
    data = get_items_from_midList_scan(midlist)
    result = get_information_hazard_non_original(data, count_threshold, reduce_threshold, non_original_mid_root_mid_dict)
    sql_insert_many(cursor, "Informationspread", "is_id", result)


def main():
    original_mid_list, non_original_mid_list, non_original_mid_root_mid_dict = get_mid_list()
    original_mid_list_new = []
    non_original_mid_list_new = []
    n = math.ceil(len(original_mid_list) / 1000)
    m = math.ceil(len(non_original_mid_list) / 1000)
    for i in range(n):
        mids = original_mid_list[i * 1000, (i + 1) * 1000]
        original_mid_list_new.append(mids)
    for i in range(m):
        mids = non_original_mid_list[i * 1000, (i + 1) * 1000]
        non_original_mid_list_new.append(mids)
    for midlist_sub in original_mid_list_new:
        profile_cal_midlist_original(midlist_sub)
    for midlist_sub_non in non_original_mid_list_new:
        profile_cal_midlist_non_original(midlist_sub_non, non_original_mid_root_mid_dict)


if __name__ == '__main__':
    main()

