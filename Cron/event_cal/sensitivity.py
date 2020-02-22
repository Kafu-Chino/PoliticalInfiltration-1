#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Hu

@time: 2020/2/18 10:10

@file: sensitivity.py
"""

import re
import ngtpy
from bert_serving.client import BertClient
import numpy as np
import os
import pandas as pd
from elasticsearch import helpers
import sys
sys.path.append('../../')
from Config.db_utils import es, pi_cur

def jinghua(text1):
    text = re.search('(.*?)//@', text1)
    if text is not None:
        text1 = text.group(1)
    re_rp = re.compile('回覆@.+?:')
    text1 = re_rp.sub('', text1)
    re_rp2 = re.compile('回复@.+?:')
    text1 = re_rp2.sub('', text1)
    re_at = re.compile('@.+?:')
    text1 = re_at.sub('', text1)
    re_at2 = re.compile('@.+?：')
    text1 = re_at2.sub('', text1)
    re_at3 = re.compile('@.+? ')
    text1 = re_at3.sub('', text1)
    re_link = re.compile('http://[a-zA-Z0-9.?/&=:]*')
    re_links = re.compile('https://[a-zA-Z0-9.?/&=:]*')
    text1 = re_link.sub("", text1)
    text1 = re_links.sub("", text1)
    if text1 in {'转发微博', '轉發微博', 'Repost', 'repost'}:
        text1 = ''
    if text1.startswith('@'):
        text1 = ''
    re_link = re.compile('t.cn/[a-zA-Z0-9.?/&=:]*')
    text1 = re_link.sub("", text1)
    re_jh = re.compile('[\u4E00-\u9FA5]|[\\w]|[,.，。！：!、?？: ]')
    text1 = re_jh.findall(text1)
    text1 = ''.join(text1)
    text1 = re.sub(' +', ' ', text1)  # 多个空格转为单个空格
    return text1


# 数据处理
def data_process(data):
    # 输入dict{mid:text}
    for mid in data:
        data[mid]['text'] = jinghua(data[mid]['text'])
    return data


# 转换bert向量
def bert_vec(texts):
    with BertClient(port=5555, port_out=5556) as bc:
        vec = bc.encode(texts)
        vec = list(vec)
    return vec


def ANN_cal(e_id, vec, y):
    index = ngtpy.Index(str(e_id)+'.anng')
    label = []
    for i in vec:
        results = index.search(i, size=8)
        sum = 0
        for j in results:
            sum += j[1]
        if sum == 0:
            pos = 0
            neg = 1
        else:
            pos = 0
            neg = 0
            for j in results:
                if y[j[0]] == 1:
                    pos += 1 - j[1] / sum
                else:
                    neg += 1 - j[1] / sum
        if pos > neg:
            label.append(1)
        else:
            label.append(0)
    return label


def create_ANN(e_id, pos_data, neg_data):
    ngtpy.create(path=str(e_id)+'.anng', dimension=768, distance_type="L2")
    index = ngtpy.Index(str(e_id)+'.anng')
    nX1 = np.array(list(pos_data['vec']))
    nX2 = np.array(list(neg_data['vec']))
    objects = np.concatenate((nX1, nX2))
    index.batch_insert(objects)
    index.build_index()
    index.save()
    y = np.concatenate((np.ones(len(nX1), dtype=int), np.zeros(len(nX2), dtype=int)))
    return y




def get_pos(POS_NUM):
    cursor = pi_cur()
    sql = 'select i_id, text from Event_information, Information where information_id = i_id group by information_id order by Count(*) DESC, hazard_index DESC'
    cursor.execute(sql)
    try:
        result = cursor.fetchall()[:POS_NUM]
    except:
        result = cursor.fetchall()
    mid = [i['i_id'] for i in result]
    texts = [i['text'] for i in result]
    return mid, texts


def get_pos_data(e_id, POS_NUM):
    if os.path.exists(e_id+'.pkl'):
        pos_data = pd.read_pickle(e_id+'.pkl')
    else:
        pos_data = pd.DataFrame(columns=('mid', 'vec'))
        mid, texts = get_pos(int(POS_NUM))
        pos_data['mid'] = mid
        pos_data['vec'] = bert_vec(texts)
        pos_data.to_pickle(e_id+'.pkl')
    return pos_data


def get_neg_data(e_index, NEG_NUM):
    NEG_NUM = int(NEG_NUM)
    query_body = {
        'query': {
            'match_all': {}
        }
    }
    es_result = helpers.scan(
        client=es,
        query=query_body,
        scroll='1m',
        index=e_index,
        timeout='1m'
    )
    neg_data = pd.DataFrame(columns=('mid', 'vec'))
    mid = []
    vec = []
    es_result = list(es_result)
    if len(es_result) > 100000:
        index_list = set(np.random.choice(range(len(es_result)),size=NEG_NUM,replace=False))
        for index, item in enumerate(es_result):
            if index not in index_list:
                continue
            mid.append(item['_source']['mid'])
            vec.append(item['_source']['text'])
        neg_data['mid'] = mid
        neg_data['vec'] = bert_vec(vec)
    else:
        index_list = set(np.random.choice(range(len(es_result)), size=int(len(es_result)/10), replace=False))
        for index, item in enumerate(es_result):
            if index not in index_list:
                continue
            mid.append(item['_source']['mid'])
            vec.append(item['_source']['text'])
        neg_data['mid'] = mid
        neg_data['vec'] = bert_vec(vec)
    return neg_data


def sensitivity(e_id,data,e_index,POS_NUM,NEG_NUM):
    data = dict_slice(data,0,1)
    data = data_process(data)
    vec = bert_vec([i['text'] for i in data.values()])
    pos_data = get_pos_data(e_id,POS_NUM)
    neg_data = get_neg_data(e_index,NEG_NUM)
    y = create_ANN(e_id, pos_data, neg_data)
    label = ANN_cal(e_id, vec, y)
    for i, j in zip(list(data.keys()), label):
        if j == 0:
            del data[i]
    return data









def dict_slice(ori_dict, start, end):
    """
    字典类切片
    :param ori_dict: 字典
    :param start: 起始
    :param end: 终点
    :return:
    """
    slice_dict = {k: ori_dict[k] for k in list(ori_dict.keys())[start:end]}
    return slice_dict