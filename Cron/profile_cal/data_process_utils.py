import re
import json
import time
import emoji
import jieba
from pandas import DataFrame
from collections import defaultdict

from data_utils import sql_insert_many
from Config.time_utils import *
from Config.db_utils import es, pi_cur, conn

def get_field(data_dict, field_name):
    field_dict = defaultdict(list)
    for k,v in data_dict.items():
        for item in v:
            field_dict[k].append(item[field_name])
    return field_dict

#对得到的微博文本进行去除链接、符号、空格等操作
def weibo_move(field_dict):
    if len(field_dict):
        text_dict = defaultdict(list)
        text_list = defaultdict(list)
        for k,v in field_dict.items():
            for item in v:
                result = Weibo_utils()
                result.remove_c_t(item)
                text = result.remove_nochn(item)
                text_list[k].append(text)
                text_dict[k].append(jieba.lcut(text,cut_all=False))
        return text_list,text_dict
    else:
        raise Exception("无微博内容")

#读取停用词
def stopwordslist():
    stopwords = set([line.strip() for line in open('stop_words.txt').readlines()])
    return stopwords

#得到微博词频 
#输入为分词后的{uid:[词列表]} 返回格式为字典{uid:{词：词频}}
def wordcount(text_dict,date):
    stopwords = stopwordslist()
    word_dict = {} #格式为字典{uid:{词：词频}}
    user_wc = {}
    thedate = datetime.date.today()
    for k,v in text_dict.items():
        word_list = {}
        count=0
        for item in v:
            for item1 in item:
                if item1 not in stopwords and item1 != " ":
                    count += 1
                    try:
                        word_list[item1] += 1
                    except:
                        word_list[item1] = 1 
        word_list["count"] = count
        word_dict[k] = word_list
    td = date + " 00:00:00"
    ta = time.strptime(td, "%Y-%m-%d %H:%M:%S")
    ts = int(time.mktime(ta))
    for k in word_dict.keys():
        word_json = json.dumps(word_dict[k])
        id = "%s_%s" % (str(int(time.time())), k)
        user_wc[id] = {
            "uid": k,
            "timestamp":ts,
            "wordcount":word_json,
            "store_date":date
        }
    sql_insert_many("WordCount", "uwc_id", user_wc)
    return word_dict

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

 
# 数据处理，包括微博过滤与分词，及分词后的词频统计
def get_processed_data(data_dict, date):
    field_dict = get_field(data_dict,"text")
    text_list, text_dict = weibo_move(field_dict)
    word_dict = wordcount(text_dict, date)
    return word_dict, text_list, text_dict


if __name__ == '__main__':
    thedate = datetime.date.today() 
    data =  {'5241560394': [{'source': '新浪', 'uid': '5241560394', 'root_uid': '', 'mid': '4404755222396058', 'root_mid': '', 'time': '2019-08-13 09:15:44', 'message_type': 1, 'sentiment': '0', 'text': '#外国人香港机场教训示威者# 看了这个视频我终于知道了什么叫:你永远滋不醒一个张嘴接尿的人http://t.cn/AiHh83xh ', 'geo': '\x08(国外未知未知)', 'net_type': '荣耀20 PRO', 'user_fansnum': 43, 'timestamp': 1565658944.0}], '6598780267': [{'source': '新浪', 'uid': '6598780267', 'root_uid': '', 'mid': '4404757026037564', 'root_mid': '', 'time': '2019-08-13 09:22:54', 'message_type': 1, 'sentiment': '-15', 'text': '#搜狐资讯#《香港机场再遭示威者瘫痪 今日余下航班全部取消》大批示威者今天聚集香港国际机场（联合早报网）海外网8月12日http://t.cn/AiHZDiWp ', 'geo': '中国移动(国外未知未知)', 'net_type': '搜狐资讯', 'user_fansnum': 3, 'timestamp': 1565659374.0}, {'source': '新浪', 'uid': '6598780267', 'root_uid': '', 'mid': '4405455973350546', 'root_mid': '', 'time': '2019-08-15 07:40:16', 'message_type': 1, 'sentiment': '-9', 'text': '#搜狐资讯#《内地记者在香港机场被示威者拘押殴打 被警方 救出》13日晚，环球网记者付国豪在香港机场被示威者非法拘押，遭到非http://t.cn/AiHiTdKD ', 'geo': '中国移动(国外未知未知)', 'net_type': '搜狐资讯', 'user_fansnum': 3, 'timestamp': 1565826016.0}]}
    word,text,text_dict = get_processed_data(data,thedate)
    print(word)
    print(text)
