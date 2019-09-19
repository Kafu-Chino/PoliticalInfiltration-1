# -- coding:utf-8 --
from elasticsearch import Elasticsearch
import pymysql  # MySQL
import redis

import jieba
import jieba.analyse

import difflib
import time, datetime

from django.db import models
import sys
sys.path.append("../../../")
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'
import django
django.setup()  # 启动django
from Mainevent.models import Event
from Mainevent.models import Hot_post


# 连接redis数据库
REDIS_HOST = '219.224.134.214'
REDIS_PORT = 6666
redis_ep = redis.Redis(connection_pool=redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0))

# 连接ES数据库
ES_HOST = '219.224.134.214'
ES_PORT = 9211
es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)


# 1.取redis set内的数据

def search_redis():
# 搜寻redis内热帖的mid list
    list_hot = []
    for i in redis_ep.zrevrangebyscore(name='Originalmid_hot',min=1000,max=100000000):
        i = str(i,encoding='utf-8')  # 解码
        list_hot.append(i)
    return list_hot  # ["mid","mid"]


# 2. 批量取评论数和转发数，绑定mid

def byte_decode(redis_set):
# 类型转换
    mid_list = []
    for i in redis_set:
        i = i.decode()
        mid_list.append(i)
    print("set解码转换完成")
    return mid_list


def combine_redis_data(mid_list):
# mid_list = ['mid1','mid2']
# 获取redis内的评论数和转发数，绑定mid
# mid存在集合里，评论数的键为mid+comment，转发数为键mid+retweeted
    comment_key = []
    retweeted_key = []
    for mid in mid_list:
        comment_key.append(mid+'comment')  # 评论数 redis key
        retweeted_key.append(mid+'retweeted')  # 转发数 redis key
    print("redis内评论转发的键列表获取完成，准备批量获取数据...")
    # 批量按顺序获取，单元素解码
    comment_list = byte_decode(redis_ep.mget(comment_key))
    retweeted_list = byte_decode(redis_ep.mget(retweeted_key))  # list [ret1, ret2]
    print("获取redis内的评论转发数完成，准备绑定mid...")
    # 绑定mid
    comment_dict = dict(zip(mid_list, comment_list))  # [mid:comment]
    retweeted_dict = dict(zip(mid_list, retweeted_list))
    # 组成一串字典list
    hot_post_list = []
    for mid in mid_list:
        hot_post_list.append({"mid": mid, "comment": int(comment_dict[mid]), "retweeted": int(retweeted_dict[mid])})
    print("评论数和转发数绑定mid完成，生成字典列表")
    return hot_post_list  # [{data},{data}], data={'mid':str,'comment':int,'retweeted':int}


# 3.判断该贴其他信息已经在热帖数据库内

def hot_post_ISinDB_Cluster(hot_post_list):
# 设置redis键mid+ISinDB，用于判断该贴其他信息已经在热帖数据库内，1在，0不在
# [{data},{data}]
    # 创建一个新的用来判断的redis集
    sets_name = "InDB_mid"
    InDB_mid_list = byte_decode(redis_ep.smembers(sets_name))  # 用于存在库的mid, ['str','mid']
    InDB_post_list = []
    New_post_list = []
    for item in hot_post_list:
        # 如果键存在，信息已经在数据库中，只需更新评论转发数
        if item["mid"] in InDB_mid_list:
            InDB_post_list.append(item)
        # 否则数据库中不存在该贴，需要插入热帖的全部信息
        else:
            New_post_list.append(item)
    return (InDB_post_list, New_post_list)  # ([{data},{data}],[{data},{data}])


# 4.热帖已经在mysql中

def update_part_db(hot_post_list):
# 只更新评论转发数
# [{data},{data}]  {data} = {"mid": 1, "comment": 1, "retweeted":1}
    for item in hot_post_list:
        # 更新数据库
        Hot_post.objects.filter(mid=item["mid"]).update(comment=item["comment"], retweeted=item["retweeted"])
    print("更新Hot_post数据库的评论转发数完毕")


# 5.热帖不在mysql中

def find_post_in_ES(hot_post_list):
# 在ES数据库中批量查询帖子的相关信息
# [{data},{data}]
    mid_list = []
    for item in hot_post_list:
        mid_list.append(item["mid"])  # 未入库热帖的mid list = [a, b]
    # 查询出mid= a 或 b 的所有数据
    query_body = {
        "query": {
            "terms": {
                "mid": mid_list
            }
        }
    }
    rs = es.search(index="weibo_all", body=query_body)
    return rs  # rs = {hits:{hits:[{"_source":{data}},{}]}}


def get_result_list(es_result, post_list):
# 剥开搜索结果的字典，取_source，返回列表, uid等,缺少comment和retweeted
# es_result = [{"_source":{data}},{}]
# post_list = [{'mid':str,'comment':int,'retweeted':int},{}]
    final_result = []
    for item in es_result:
        for post in post_list:
            if item['_source']["mid"] == post["mid"]:
                item['_source']["comment"] = post["comment"]
                item['_source']["retweeted"] = post["retweeted"]
                final_result.append(item['_source'])  # item是个字典,ES的每条数据
    print("从ES数据流获取新热帖的相关信息，操作完成")
    return final_result  # [{data},{}]
    #{data} = {"uid":1, "timestamp", "comment", "root_uid", "text", "mid",
    # "ip", "keywords_dict", "message_type", "retweeted", "root_mid", ...}


def hotpost_get_keyword(hot_post):
# 单热帖关键词获取
# hot_post_list = [{data},{}]
# hot_post = {data}
    text = hot_post["text"]
    # 参数为文本，重要性从高到低返回关键词的数量，是否同时返回每个关键词的权重,词性过滤仅提取地名 名词 动名词 动词
    keywords_list = jieba.analyse.textrank(text, topK=20, withWeight=False,
                                           allowPOS=('ns', 'n', 'vn', 'v'))
    print("关键词分词完成")
    return keywords_list  # list ['地址', '下载']


def get_hotpost_related_event(hot_post, query_table="Event"):
# 单热帖关键词调出query_table库中的相似事件
# hot_post_list = [{data},{}]
# hot_post = {data}
    # 1.调出热帖关键词
    keywords_dict = hot_post["keywords_dict"]  # 取keywords_dict列  models.
    # 2.调出相关事件
    similar_event = Event.objects.all().values_list("e_id","event_name")  # QuerySet类型
    similar_event_list = list(similar_event)  # list [(1,2), (元组)]
    similar_event = dict(similar_event_list)  # dic {1: 2, 3: 'jiqw', 2: 1372}
    print(hot_post["mid"],"的相似事件计算完毕")
    return similar_event


def insert_into_db(final_result, come_from="weibo_"):
# 插入热帖的全部信息, 热帖列表入库
# [{data},{}]
    querysetlist = []
    pipe = redis_ep.pipeline()  # 批量存入redis数据
    for data in final_result:
        data["h_id"] = come_from + data["mid"]  # 主键
        data["date"] = datetime.datetime.utcfromtimestamp(data["timestamps"]).strftime("%Y-%m-%d")  # 时间戳转为datetime, 再转为这样的存储格式
        data["source"] = come_from  # 来源
        data["store_timestamp"] = int(time.time())  # 获取当前时间戳
        data["store_date"] = datetime.datetime.now().strftime("%Y-%m-%d")  # 获取当前日期
        data["keywords_dict"] = ",".join(hotpost_get_keyword(data))  # 热帖关键词获取
        data["similar_event"] = get_hotpost_related_event(data, "Event")  #相似事件
        one_post = Hot_post(
            h_id=data["h_id"],
            uid=data["uid"],
            root_uid=data["root_uid"],
            mid=data["mid"],
            comment=data["comment"],
            retweeted=data["retweeted"],
            text=data["text"],
            keywords_dict=data["keywords_dict"],
            timestamp=data["timestamps"],
            date=data["date"],
            ip=0,  # ES和redis都没有值
            geo=data["geo"],
            message_type=data["message_type"],
            root_mid=data["root_mid"],
            source=data["source"],
            store_timestamp=data["store_timestamp"],
            store_date=data["store_date"],
            similar_event=data["similar_event"],
        )
        #querysetlist.append(Hot_post(**data))  # 部分data的键值对需要删除，因此不用该方法
        querysetlist.append(one_post)  # [{Hot_post.objects对象}]
        pipe.sadd('InDB_mid', data['mid'])  # 向redis新增一个集合名为InDB_mid，用于判断是否在库
    print("已插入%d条新热帖到数据库:" % len(querysetlist))
    Hot_post.objects.bulk_create(querysetlist)  # 使用django.db.models.query.QuerySet.bulk_create()批量创建对象，减少SQL查询次数
    pipe.execute()  # 执行redis 添加操作
    print("新热帖写入数据库完毕，redis更新在库集合完毕")


if __name__ == '__main__':
    time_start = time.time()
    print("程序开始\n")

    mid_list = search_redis()   # 热帖的mid list  ['mid1','mid2'] = ['44063', '440544']
    hot_post_list = combine_redis_data(mid_list)
    (InDB_post_list, New_post_list) = hot_post_ISinDB_Cluster(hot_post_list) # 分成已在数据库的，不在数据库的
    # 该贴已经存在数据库，只更新评论转发数
    if len(InDB_post_list) != 0:
        print("现在有%d条已经存在数据库，更新其评论转发数" % len(InDB_post_list)) 
        update_part_db(InDB_post_list)
        print("成功更新评论转发数")
    # 不在数据库，需要插入全部信息
    # 得到热帖相关数据
    if len(New_post_list) != 0:
        rs = find_post_in_ES(New_post_list)
        final_result = get_result_list(rs['hits']['hits'], New_post_list)  # 得到完整数据列表[{data},{}]
        print("从ES获取新贴的相关数据信息完毕，执行写入数据库操作...")
        # 插入数据库
        insert_into_db(final_result, come_from="weibo_")
    print("本次redis读写操作完成\n")

    print("程序结束,Finish cost seconds:", time.time()-time_start)