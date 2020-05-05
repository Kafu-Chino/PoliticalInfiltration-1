#!/usr/bin/env python
# -- coding: utf-8 --
# @Time : 2020/4/22 16:00
# Author : Hu
# File : extend_cal_main.py

import random
import sys
sys.path.append("../../")
from Config.db_utils import get_event_para
from Cron.event_cal.data_utils import store_event_para
from Cron.event_cal.sensitivity import sensitivity
from Cron.event_cal.sensitive_word_filter import sensitive_word_filter
from Cron.extend_cal.data_utils import *


def extend_cal_main(e_id):
    """
    事件信息扩线主函数
    :param e_id:事件id
    :return:None
    """
    try:
        POS_NEG = get_event_para(e_id, 'pos_neg')
    except:
        POS_NEG = 50
        store_event_para(e_id, 'pos_neg')

    try:
        EXTEND_SCALE = get_event_para(e_id, 'extend_scale')
    except:
        EXTEND_SCALE = 10
        store_event_para(e_id, 'extend_scale')

    # 获取人工添加信息数
    add_num = get_add_num(e_id)
    update_process_status(e_id, 1)    # 把上次审核入库的正类信息标记为已处理
    # 获取事件信息
    e_name, e_index = get_event_p(e_id)
    # 敏感词过滤
    print('敏感词过滤')
    data_dict = sensitive_word_filter(0, e_id, 1)
    print(len(data_dict))
    # 扩线计算
    print('扩线计算')
    if data_dict:
        data_dict = sensitivity(e_id, data_dict, e_index, POS_NEG, 1)
    print(len(data_dict))
    # 去重
    if data_dict:
        mid = set(data_dict.keys())
        # 获取事件已有敏感信息mid
        mid_remove = get_mid_info(e_id)
        # 获取事件已在扩线新增信息库中的mid
        mid_remove.extend(get_mid_extend(e_id))
        mid_remove = set(mid_remove)
        # 去掉重复
        mid = list(mid - mid_remove)
        l = len(mid)
        print(l)
        # 根据添加数选取适量信息
        if l:
            add_num = add_num * int(EXTEND_SCALE)
            if l > add_num:
                mid = random.choices(mid, k=add_num)
            # for i in data_dict:
            #     if i not in mid:
            #         del data_dict[i]
            # 入扩线新增信息库
            if len(mid):
                store_extend_info(e_id, mid, data_dict)

