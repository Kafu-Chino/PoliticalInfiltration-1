#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Hu

@time: 2020/1/15 14:37

@file: user_sentiment.py
"""

from data_get_utils import sql_insert_many
from Config.db_utils import pi_cur
from Config.time_utils import today, nowts
import pickle
import joblib
from sentiment_classifier import triple_classifier
from collections import Counter

cursor = pi_cur()


def cal_user_emotion(word_dict):
    '''
    用户情感计算函数  0为负面 1为中性 2为正面
    :param word_dict:
    :return:None
    '''
    # 加载词向量
    with open('sentiment_model_data/weibo_vector.pkl', 'rb') as f:
        weibo_dic = pickle.load(f)
    # 加载模型
    l_m = joblib.load('sentiment_model_data/sentiment_logical.model')
    user_sentiment_dict = {}
    for uid, weibo_list in word_dict.items():#value 为列表  key 为uid
        sentiment_dict = {}
        thedate = today()
        sum_r = len(weibo_list)
        if sum_r :#此天有微博数据
            sentiment = triple_classifier(weibo_list, weibo_dic, l_m)
            c = Counter(sentiment).most_common()
            c = dict(c)
            sentiment_dict['timestamp'] = nowts()
            sentiment_dict['uid'] = uid
            sentiment_dict['negtive'] = c.get('0', 0)
            sentiment_dict['nuetral'] = c.get('1', 0)
            sentiment_dict['positive'] = c.get('2', 0)
            sentiment_dict['store_date'] = thedate
            user_sentiment_dict['%s_%s'% (str(sentiment_dict['timestamp']), uid)] = sentiment_dict
        else:
            sentiment_dict['timestamp'] = nowts
            sentiment_dict['uid'] = uid
            sentiment_dict['negtive'] = 0
            sentiment_dict['nuetral'] = 0
            sentiment_dict['positive'] = 0
            sentiment_dict['store_date'] = thedate
            user_sentiment_dict['%s_%s' % (str(sentiment_dict['timestamp']), uid)] = sentiment_dict
            print("no data")
    sql_insert_many(cursor, "UserSentiment", "us_id", user_sentiment_dict)