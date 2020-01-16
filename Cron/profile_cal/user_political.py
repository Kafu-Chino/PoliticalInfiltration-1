#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Hu

@time: 2020/1/15 21:17

@file: user_political.py
"""

import csv
from data_get_utils import sql_insert_many
from Config.db_utils import pi_cur, conn
from Config.time_utils import today, nowts
from decimal import *

cursor = pi_cur()
POLITICAL_LABELS = ['left', 'right', 'mid']
political_bias_dict = {'left': '左倾', 'mid': '中立', 'right': '右倾'}
LEFT_STA = 6000
RIGHT_STA = 3000


def load_word():  # 加载词典
    domain_dict = dict()
    for name in POLITICAL_LABELS:
        word_dict = dict()
        reader = csv.reader(open('political_bias_word_dict/%s.csv' % name, 'r'))
        for count, word in reader:
            word = word.strip('\r\t\n')
            count = count.strip('\r\t\n')
            word_dict[word] = Decimal(str(count))
        domain_dict[name] = word_dict
    return domain_dict


DOMAIN_DICT = load_word()


def com_p(word_list,domain_dict):
    p = 0
    test_word = set(word_list.keys())
    train_word = set(domain_dict.keys())
    c_set = test_word & train_word
    p = sum([Decimal(domain_dict[k])*Decimal(word_list[k]) for k in c_set])
    return p


def political_classify(uid_weibo):
    '''
    用户政治倾向分类主函数
    输入数据示例：
    uid_weibo:分词之后的词频字典  {uid1:{'key1':f1,'key2':f2...}...}

    输出数据示例：
    domain：政治倾向标签字典
    {uid1:label,uid2:label2...}
    '''
    domain_dict = dict()
    r_domain = dict()
    for k,v in uid_weibo.items():
        if not len(v):
            domain_dict[k] = 'mid'
            return domain_dict
        dis = 0
        l = 'mid'
        r_dict = dict() #存储用户语料 与 每种倾向 的权重比值
        for la in POLITICAL_LABELS:
            re_weight = com_p(DOMAIN_DICT[la],v) #比较用户词频字典 和 语料库词频字典 相同词的个数
            r_dict[la] = re_weight
            if la == 'left' and re_weight >= LEFT_STA and re_weight > dis:
                dis = re_weight
                l = la
            if la == 'right' and re_weight >= RIGHT_STA and re_weight > dis:
                dis = re_weight
                l = la
        domain_dict[k] = l #存储最终政治倾向（）
        r_domain[k] = r_dict#存储各个政治倾向的权值

    return domain_dict


def get_user_political(word_dict):
    '''
    用户政治倾向计算函数  left为左倾 mid为中立 right为右倾
    :param word_dict:
    :return:None
    '''
    political = political_classify(word_dict)
    sql = 'UPDATE Figure SET political=%s where uid=%s'
    val = []
    for i, j in political.items():
        val.append((j, i))
    # 执行sql语句
    n = cursor.executemany(sql, val)
    print("update %d success" % n)
    conn.commit()