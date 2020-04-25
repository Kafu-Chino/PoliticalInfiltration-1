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
from collections import OrderedDict
from elasticsearch import helpers
import sys
import math
from warnings import filterwarnings
import pymysql
filterwarnings("ignore",category=pymysql.Warning)

sys.path.append('../../')
from Config.db_utils import ees, pi_cur, conn
from Config.base import BERT_HOST, BERT_PORT, BERT_PORT_OUT
from Config.time_utils import *
from Cron.event_cal.data_utils import event_es_save


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
    mid_texts = []
    for mid in list(data.keys()):
        text = jinghua(data[mid]['text']).strip()
        if text != '':
            mid_texts.append((mid,text))
        else:
            del data[mid]
    return data, mid_texts


# 转换bert向量
def bert_vec(texts):
    with BertClient(ip=BERT_HOST, port=BERT_PORT, port_out=BERT_PORT_OUT) as bc:
        vec = bc.encode(texts)
        vec = list(vec)
    return vec


# 搜索转换
def bert_vec_quick(mid_texts):
    mid_dict = OrderedDict()
    for i in mid_texts:
        mid_dict[i[0]] = {'text': i[1]}
    # 从es获取
    result = ees.mget(index='information_vector', body={'ids': list(mid_dict.keys())})['docs']
    for item in result:
        if item['found']:
            mid_dict[item['_source']['mid']]['vec'] = np.array(item['_source']['vector'])

    # 没有的处理
    mid_no = []
    texts = []
    for i in mid_dict:
        if mid_dict[i].get('vec', None) is None:
            mid_no.append(i)
            texts.append(mid_dict[i]['text'])
    if mid_no:
        no_vec = bert_vec(texts)
        # 存储进es
        t = nowts()
        save = []
        for i,j in zip(mid_no, no_vec):
            mid_dict[i]['vec'] = j
            message = {}
            message['mid'] = i
            message['vector'] = j.tolist()
            message['timestamp'] = t
            save.append(message)
        event_es_save(save, 'information_vector')
    vec = [mid_dict[i]['vec'] for i in mid_dict]
    return vec


def ANN_cal(index, vec, y):
    # index = ngtpy.Index(str(e_id) + '.anng')
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


def create_ANN(e_id, pos_data, neg_data, is_extend):
    if is_extend:
        ngtpy.create(path=str(e_id) + '_extend.anng', dimension=768, distance_type="L2")
        index = ngtpy.Index(str(e_id) + '_extend.anng')
    else:
        ngtpy.create(path=str(e_id) + '.anng', dimension=768, distance_type="L2")
        index = ngtpy.Index(str(e_id) + '.anng')
    nX1 = np.array(list(pos_data['vec']))
    nX2 = np.array(list(neg_data['vec']))
    objects = np.concatenate((nX1, nX2))
    index.batch_insert(objects)
    index.build_index()
    y = np.concatenate((np.ones(len(nX1), dtype=int), np.zeros(len(nX2), dtype=int)))
    return index, y


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


def get_pos_quick(e_id):
    cursor = pi_cur()
    sql = 'select * from EventPositive where e_id="%s"' %e_id
    cursor.execute(sql)
    result = cursor.fetchall()
    pos_num = len(result)
    texts = [item['text'] for item in result]
    vec = [np.frombuffer(item['vector'],dtype=np.float32) for item in result]
    # print(text)
    # print(vec)
    return pos_num, texts, vec


def store_pos(e_id, pos_data):
    cursor = pi_cur()
    t = nowts()
    sql = 'insert into EventPositive set e_id=%s,text=%s,vector=%s,store_timestamp=%s,store_type=0,process_status=1'
    val = []
    for index, row in pos_data.iterrows():
        val.append((e_id, row['text'], row['vec'].tostring(), t))
    # 执行sql语句
    n = cursor.executemany(sql, val)
    print("事件相关正类入库成功 %d 条" % n)
    conn.commit()


def get_pos_data(e_id, POS_NUM):
    pos_data = pd.DataFrame(columns=('text', 'vec'))
    pos_num, texts, vec = get_pos_quick(e_id)
    if pos_num != 0:
        pos_data['text'] = texts
        pos_data['vec'] = vec
    else:
        pos_num = POS_NUM
        mid, texts = get_pos(int(POS_NUM))
        pos_data['text'] = texts
        pos_data['vec'] = bert_vec(texts)
        # pos_data.to_pickle(e_id + '.pkl')
        store_pos(e_id, pos_data)
    return pos_data, pos_num


def get_neg_data(e_index, NEG_NUM):
    NEG_NUM = int(NEG_NUM)
    query_body = {
        'query': {
            'match_all': {}
        }
    }
    es_result = helpers.scan(
        client=ees,
        query=query_body,
        scroll='1m',
        index=e_index,
        timeout='1m'
    )
    neg_data = pd.DataFrame(columns=('mid', 'vec'))
    mid = []
    vec = []
    mid_texts = []
    es_result = list(es_result)
    if len(es_result) > NEG_NUM * 8:
        index_list = set(np.random.choice(range(len(es_result)), size=NEG_NUM, replace=False))
        for index, item in enumerate(es_result):
            if index not in index_list:
                continue
            mid.append(item['_source']['mid'])
            vec.append(item['_source']['text'])
            mid_texts.append((item['_source']['mid'],item['_source']['text']))
        neg_data['mid'] = mid
        neg_data['vec'] = bert_vec_quick(mid_texts)
    else:
        index_list = set(np.random.choice(range(len(es_result)), size=int(len(es_result) / 8), replace=False))
        for index, item in enumerate(es_result):
            if index not in index_list:
                continue
            mid.append(item['_source']['mid'])
            vec.append(item['_source']['text'])
            mid_texts.append((item['_source']['mid'],item['_source']['text']))
        neg_data['mid'] = mid
        neg_data['vec'] = bert_vec_quick(mid_texts)
    return neg_data


def sensitivity(e_id, data, e_index, POS_NEG, is_extend):
    """
    敏感计算主函数
    :param e_id: 事件id
    :param data: 事件数据
    :param e_index: 事件索引
    :param POS_NEG: 敏感计算负类比正类比例
    :param is_extend: 是否为扩线任务
    :return: 敏感数据
    """
    # data = dict_slice(data, 0, 25)   # 测试代码，采样一小部分数据
    data, mid_texts = data_process(data)
    POS_NUM = 1000
    pos_data, pos_num = get_pos_data(e_id, POS_NUM)
    NEG_NUM = pos_num * POS_NEG
    neg_data = get_neg_data(e_index, NEG_NUM)
    index, y = create_ANN(e_id, pos_data, neg_data, is_extend)
    batch_num = 12800
    batch_all = math.ceil(len(mid_texts) / batch_num)
    label = []
    for batch_epoch in range(batch_all):
        texts_batch = mid_texts[batch_epoch * batch_num: (batch_epoch + 1) * batch_num]
        print("文本{}至{}， 共{}".format(batch_epoch * batch_num, (batch_epoch + 1) * batch_num, len(mid_texts)))
        vec = bert_vec_quick(texts_batch)
        label_batch = ANN_cal(index, vec, y)
        label.extend(label_batch)
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
    :return: 切片后结果
    """
    slice_dict = {k: ori_dict[k] for k in list(ori_dict.keys())[start:end]}
    return slice_dict


def main():
    data = {'mid1':{'text':'封了号，删了消息，禁言了，就能高枕无忧？事实上传递消息的里面也有持正面态度的，一起杀？一起禁？同样一件事如果得到广泛的讨论，得出结论可能更接近事实，今天一言堂的后果，不就是大家用另一种方式来传播了吗？'},
            'mid2':{'text':'今天在fb上看了直播，，没有一百多万也不只十几万，，应该是几十万  把几十万人都认为被外部势力挑动 这个理由有点牵强'},
            'mid3':{'text':' 因为内地有死刑，且常规情况量刑更重执行更严...//@陈琛CHENC:先了解他们为什么游行.因为要颁布一条法令 部分香港犯罪分子要引渡到国内审判，请问这有什么问题？？香港人是不是不知道自己是中国的一部分？？还有10几年你们使劲跳[微笑]'},
            'mid4':{'text':'#外交部回应香港游行#为什么我什么都不知道 '},
            'mid5':{'text':'很多人为反对而反对而已//@不是不是大明湖畔夏雨荷的女儿:你们真的看了么[微笑] 修改原因是某香港人在台湾杀人  因为香港台湾没有签协议 所以不能移交到香港审讯  所以补充类似发生这样的事情  就移交大陆审讯  眼睛是个好东西不要盲目跟风 谁被洗脑谁知道[微笑] http://t.cn/AiCCGOOx'},}
    n_data = sensitivity('test_abc',data,'weibo_all',10,10)
    print(n_data)


if __name__ == '__main__':
    main()