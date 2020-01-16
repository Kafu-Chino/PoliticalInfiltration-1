#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Hu

@time: 2019/12/22 10:34

@file: sentiment_classifier.py
"""
import numpy as np


def get_vector(text, word_dic):
    count = 0
    article_vector = np.zeros(300)
    for cutWord in text:
        if word_dic.get(cutWord, 0) != 0:
            article_vector += word_dic[cutWord]
            count += 1
    return article_vector / count


def triple_classifier(weibo, weibo_dic, l_m):
    X = [get_vector(i, weibo_dic) for i in weibo]
    new_label = []
    for i in l_m.predict_proba(X):
        if i[1] < 0.3:
            new_label.append('0')
        elif i[1] > 0.7:
            new_label.append('2')
        else:
            new_label.append('1')

    print(new_label)