#!/usr/bin/env python
# -- coding: utf-8 --
# @Time : 2020/4/25 20:05
# Author : Hu
# File : data_utils.py

import sys
sys.path.append("../../")
from Config.db_utils import pi_cur, conn


def get_event_p(e_id):
    sql = "select event_name,es_index_name from Event where e_id = '{}'".format(e_id)
    cursor = pi_cur()
    cursor.execute(sql)
    results = cursor.fetchall()[0]
    return results['event_name'], results['es_index_name']


def get_mid_info(e_id):
    """
    获取事件已有敏感信息的mid
    :param e_id: 该事件e_id
    :return: mid
    """
    sql = "select information_id from Event_information where e_id = '{}'".format(e_id)
    cursor = pi_cur()
    cursor.execute(sql)
    results = cursor.fetchall()
    mid = [i['information_id'][2:] for i in results]
    return mid


def get_mid_extend(e_id):
    """
    获取事件已在扩线新增库里的mid
    :param e_id: 该事件e_id
    :return: mid
    """
    sql = "select mid from ExtendReview where e_id = '{}'".format(e_id)
    cursor = pi_cur()
    cursor.execute(sql)
    results = cursor.fetchall()
    mid = [i['mid'] for i in results]
    return mid


def get_add_num(e_id):
    """
    获取人工添加的文本数
    :param e_id: 该事件e_id
    :return: add_num
    """
    sql = "select id from EventPositive where e_id = '{}' and store_type = 1 and process_status = 0".format(e_id)
    cursor = pi_cur()
    cursor.execute(sql)
    add_num = len(cursor.fetchall())
    return add_num


def store_extend_info(e_id, mid, data_dict):
    """
    存储至扩线新增库
    :param e_id: 相关事件id
    :param mid: 信息id
    :param data_dict: 数据
    :return: None
    """
    cursor = pi_cur()
    sql = 'replace into ExtendReview set ie_id=%s,e_id=%s,uid=%s,root_uid=%s,mid=%s,' \
          'text=%s,timestamp=%s,send_ip=%s,geo=%s,message_type=%s,root_mid=%s,' \
          'source=%s,process_status=0'
    val = []
    for i, j in data_dict.items():
        val.append((e_id+i,e_id,j.get('uid',None),j.get('root_uid',None),i,j.get('text',None),
                    j.get('timestamp',None),j.get('send_ip',None),j.get('geo',None),
                    j.get('message_type',None),j.get('root_mid',None),j.get('source',None)))
    # 执行sql语句
    n = cursor.executemany(sql, val)
    print("入扩线新增库成功 %d 条" % n)
    conn.commit()


def get_edic_extend():
    cursor = pi_cur()
    sql = 'select e_id from ExtendTask where cal_status = 0'
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def update_cal_status(eid_dict, cal_status):
    cursor = pi_cur()
    sql = "UPDATE ExtendTask SET cal_status = %s WHERE e_id = %s"

    params = [(cal_status, item['e_id']) for item in eid_dict]
    cursor.executemany(sql, params)
    conn.commit()