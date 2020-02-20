#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Hu

@time: 2020/2/17 13:44

@file: SentimentalPolarities.py
"""

import sys
import re
import numpy as np
import jieba
import pickle
import joblib
sys.path.append("../../")
from Config.db_utils import es, pi_cur, conn


# 对得到的微博文本进行去除链接、符号、空格等操作
def weibo_move(data):
    if len(data):
        cut_list = []
        stopwords = set([line.strip() for line in open('../profile_cal/stop_words.txt', 'r', encoding='utf-8').readlines()])
        for item in data:
            result = Weibo_utils()
            result.remove_c_t(item)
            text = result.remove_nochn(item)
            cutWords = [k for k in jieba.cut(text) if k not in stopwords and k!=' ']
            cut_list.append(cutWords)
        return cut_list
    else:
        raise Exception("无微博内容")


class Weibo_utils:
    def __init__(self):
        self.re_comment = re.compile("回复@.*?:")   # 匹配评论链
        self.re_link = re.compile('http://[a-zA-Z0-9.?/&=:]*')   # 匹配网址
        self.re_links = re.compile('https://[a-zA-Z0-9.?/&=:]*')   # 匹配网址
        self.re_text = re.compile(r'[^\u4e00-\u9fa5^ ^a-z^A-Z]')   # 匹配中文空格与英文

    # 删除转发评论链
    def remove_c_t(self,text):
        text = self.re_comment.sub("", text)   # 删除转发评论链
        text = self.re_link.sub("", text)
        text = self.re_links.sub("", text)
        text = text.split("//@",1)[0]
        text = text.strip()
        if text in set(['转发微博','轉發微博','Repost','repost']):
            text = ''
        return text

    # 移除非中英文及空格
    def remove_nochn(self, text):
        text = self.re_text.sub("", text)
        return text


# 处理输入数据
def data_process(data):
    mid = data.keys()
    text = data.values()
    # 预处理,分词
    cut_list = weibo_move(text)
    return mid, cut_list


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


def triple_classifier(mid, weibo, weibo_dic, l_m, SENTIMENT_POS, SENTIMENT_NEG):
    X = [get_vector(i, weibo_dic) for i in weibo]
    result = {}
    for i, j in zip(l_m.predict_proba(X),mid):
        if i[1] < SENTIMENT_NEG:
            result[j] = '-1'
        elif i[1] > SENTIMENT_POS:
            result[j] = '1'
        else:
            result[j] = '0'
    return result


# 情感极性计算
def sentiment_polarities(data, SENTIMENT_POS, SENTIMENT_NEG):
    mid, cut_list = data_process(data)
    # 加载词向量
    with open('../profile_cal/sentiment_model_data/weibo_vector.pkl', 'rb') as f:
        weibo_dic = pickle.load(f)
    # 加载模型
    l_m = joblib.load('../profile_cal/sentiment_model_data/sentiment_logical.model')
    result = triple_classifier(mid, cut_list, weibo_dic, l_m, SENTIMENT_POS, SENTIMENT_NEG)
    return result


def main():
    data = {'1234334':'封了号，删了消息，禁言了，就能高枕无忧？事实上传递消息的里面也有持正面态度的，一起杀？一起禁？同样一件事如果得到广泛的讨论，得出结论可能更接近事实，今天一言堂的后果，不就是大家用另一种方式来传播了吗？','2765672':'刚刚读到的一篇文章《香港人在怕什么？》对啊，百万香港民众街头示威因为新的引渡条例？ 在很多家庭都住在狭窄房子里的都市这么多人却在关心有钱人的死活。悲哀 '}
    result = sentiment_polarities(data)
    print(result)


if __name__ == '__main__':
    main()