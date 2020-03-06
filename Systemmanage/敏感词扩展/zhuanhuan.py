#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Hu

@time: 2019/11/22 12:52

@file: zhuanhuan.py
"""

from .opencc.opencc import OpenCC
from pypinyin import lazy_pinyin


cc = OpenCC('s2hk')
cc2 = OpenCC('hk2s')


def hk2s(string):
    return cc.convert(string)

# print(hk2s('台湾wan'))


def s2hk(string):
    return cc2.convert(string)


def get_acronym(str_data):
    return "".join([i[0][0] for i in lazy_pinyin(str_data)])
# print(get_acronym('台湾wan'))


def get_pinyin(str_data):
    return "".join([i for i in lazy_pinyin(str_data)])


# s_w = []
# with open('sensitive_words_list_add.txt','r',encoding='utf-8') as f:
#     for i in f.readlines():
#         s_w.append(i.strip())
#
# f_s = [hk2s(i) for i in s_w if hk2s(i)!=i]
# szm_s = [get_acronym(i) for i in s_w if not i.encode('utf-8').isalpha()]
#
# with open('fanti_sw.txt','w',encoding='utf-8') as f1:
#     for i in f_s:
#         f1.write(i+'\n')
#
# with open('szm_sw.txt','w',encoding='utf-8') as f2:
#     for i in szm_s:
#         f2.write(i+'\n')