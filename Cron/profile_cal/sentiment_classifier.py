#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Hu

@time: 2019/12/22 10:34

@file: sentiment_classifier.py
"""
import numpy as np
from sklearn.preprocessing import Imputer

def get_vector(text, word_dic):
    count = 0
    article_vector = np.zeros(300)
    for cutWord in text:
        if word_dic.get(cutWord, 0) != 0:
            article_vector += word_dic[cutWord]
            count += 1
    if count:
        return article_vector / count
    else:
        return article_vector


def triple_classifier(weibo, weibo_dic, l_m):
    X = [get_vector(i, weibo_dic) for i in weibo]
    # X = Imputer().fit_transform(X)
    # print(X)
    new_label = []
    for i in l_m.predict_proba(X):
        if i[1] < 0.2:
            new_label.append('0')
        elif i[1] > 0.7:
            new_label.append('2')
        else:
            new_label.append('1')

    return new_label