#!/usr/bin/env python
# -- coding: utf-8 --
# @Time : 2020/4/28 17:58
# Author : Hu
# File : extend_task.py

from bert_serving.client import BertClient
import sys
sys.path.append('../../')
from Cron.extend_cal.data_utils import get_edic_extend, update_cal_status
from Cron.extend_cal.extend_cal_main import extend_cal_main


# 对新添加的扩线任务进行计算
def extend():
    # 获取新添加的扩线任务（计算状态为0）
    eid_dic = get_edic_extend()

    # 更新为“计算中”
    update_cal_status(eid_dic, 1)

    # 分事件进行计算
    print("需要计算事件 {} 个。".format(len(eid_dic)))
    for e_item in eid_dic:
        e_id = e_item['e_id']

        # 事件扩线计算
        extend_cal_main(e_id)

        # 更新为“计算完成”
        update_cal_status([e_item], 2)

        print("事件 %s 扩线完成。" % e_id)


if __name__ == '__main__':
    extend()