#!/usr/bin/env python
# -- coding: utf-8 --
# @Time : 2020/2/12 21:52
# Author : Hu
# File : event_semantic.py

import sys
import re
import emoji
import jieba
from gensim import corpora, models
import random
sys.path.append("../../")
from Config.db_utils import es, pi_cur, conn
import time
WEIBO_NUM = 100000
cursor = pi_cur()


#对得到的微博文本进行去除链接、符号、空格等操作
def weibo_move(data):
    if len(data):
        cut_list = []
        stopwords = set([line.strip() for line in open('stop_words.txt', 'r', encoding='utf-8').readlines()])
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
    if len(data) > WEIBO_NUM:
        data = random.choices(data, k=WEIBO_NUM)
    # 预处理,分词
    cut_list = weibo_move(data)
    dictionary = corpora.Dictionary(cut_list)
    corpus = [dictionary.doc2bow(text) for text in cut_list]
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    return corpus_tfidf, dictionary


# 事件LDA聚类
def lda_analyze(corpusTfidf, dictionary, num_topics=10, iterations=50, workers=6, passes=1):
    lda_multi = models.ldamulticore.LdaMulticore(corpus=corpusTfidf, id2word=dictionary, num_topics=num_topics, \
                                                 iterations=iterations, workers=workers, batch=True,
                                                 passes=passes)  # 开始训练
    print(lda_multi.print_topics(num_topics, 10))  # 输出主题词矩阵


# 事件语义分析
def event_semantic(data):
    corpus_tfidf, dictionary = data_process(data)
    lda_analyze(corpus_tfidf, dictionary, num_topics=3)


def main():
    st = time.time()
    sql = 'select text from Information'
    cursor.execute(sql)
    result = cursor.fetchall()
    data = []
    for i in result:
        data.append(i['text'])
    print(len(data))
    # data = ['置顶 疫情蔓延，面对生活给我们如此严肃的提问，应该如何回答？我们以#VOGUE三月号# @李宇春 封面告诉大家，只要心里保存热爱，希望便不可摧毁。和所有中国人一样面临命运新考验的李宇春，决定以歌唱来回应，她写下心系疫区的《岁岁平安》，委婉温情中透着刚强，启发每个人以自己的方式去继续。对音乐、时尚、艺术、创意都充满热爱的李宇春，对未来还有很多梦想和憧憬，我们和她一样相信，#有坚持有希望#。💪 #VOGUE战疫进行时#  摄影：Nick Knight 造型：Daniela Paudice', '如果可以和未来的你通一个电话，你想和他（她）说什么？#陈飞宇情人节电话打给谁# ？想知道他说了什么吗？敬请期待 2月14日正式上线的芭莎珠宝电子刊“陈飞宇 2020的未知来电”！预售已开启，这个非常时期的0214情人节“宇”爱同行，愿这份温暖驱散寒冷和阴霾。@陈飞宇Arthur @陈飞宇工作室 @陈飞宇全国后援会 陈飞宇珠宝//@Pomellato宝曼兰朵']
    event_semantic(data)
    et = time.time()
    print(st-et)


if __name__ == '__main__':
    main()
