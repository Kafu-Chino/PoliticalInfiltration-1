import sys
sys.path.append('../../')
from Config.base import *
import time


a=time.time()


def find_hotmid():
    #找到热帖id
    list_hot = []
    for i in redis_ep.zrevrangebyscore(name='Originalmid_hot',min=1000,max=100000000):
        i = str(i,encoding='utf-8')
        list_hot.append(i)
    print(time.time()-a)
    return  list_hot


def search_es(query_body):
    #查询es数据库
    query = es.search(index="weibo_all",body=query_body,scroll='5m',size = 10000)
    results = query['hits']['hits']  # es查询出的结果第一页
    total = query['hits']['total']  # es查询出的结果总量
    scroll_id = query['_scroll_id']  # 游标用于输出es查询出的所有结果
    list = []
    for line in results:
        list.append(line['_source'])
    yield list

    for i in range(0, int(total / 10000) ):
        # scroll参数必须指定否则会报错
        query_scroll = es.scroll(scroll_id=scroll_id, scroll='5m')['hits']['hits']
        list = []

        for line in query_scroll:
            list.append(line['_source'])
        yield list


def save_hotmid(list_hot):
    #将热帖id存入redis
    with redis_ep.pipeline(transaction=False) as p:
        for mid in list_hot:
            p.sadd('hot_post',mid)
        p.execute()
    print(redis_ep.scard('hot_post'))


def save_hotuid(list_hot):
    #将热帖id对应的uid存入redis
    hot_uid = []
    query_body1 = {
        "query": {
            "terms": {
                "mid": list_hot
            }
        }

    }
    for list2 in search_es(query_body1):
        for line in list2:
            hot_uid.append(line['uid'])
    redis_ep.sadd('hot_uid', *list(set(hot_uid)))
    print(redis_ep.scard('hot_uid'))


def save_relateduid(list_hot):
    #将所有对热贴评论和转发的uid存入redis
    for mid in list_hot:
        query_body2 = {
            "query": {
                "term": {
                    "root_mid": mid
                }
            }

        }
        for list1 in search_es(query_body2):
            list_uid = []
            for line in list1:
                list_uid.append(line['uid'])
            # print(len(list_uid))
            redis_ep.sadd(mid, *list(set(list_uid)))
        print(redis_ep.scard(mid))


def main():
    list_hot = find_hotmid()
    save_hotmid(list_hot)
    save_hotuid(list_hot)
    save_relateduid(list_hot)
    print(time.time() - a)


if __name__ == '__main__':
    main() 
