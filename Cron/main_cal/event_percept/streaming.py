import  sys
sys.path.append('../../')
from Config.base import *
import multiprocessing
import random
import time

start_time=time.time()


def data_query():
    #从es数据库中取数据
    query_body = {
        "query":{
            "match_all":{},
                    },
        "sort":{
            "timestamps":{
                "order":"asc"
            }
        },
     }

    query = es.search(index="weibo_all",body=query_body,scroll='5m',size = 5000)

    results = query['hits']['hits'] # es查询出的结果第一页
    total = query['hits']['total']  # es查询出的结果总量
    scroll_id = query['_scroll_id'] # 游标用于输出es查询出的所有结果

    for i in range(0, int(total/5000)+1):
        # scroll参数必须指定否则会报错
        query_scroll = es.scroll(scroll_id=scroll_id,scroll='5m')['hits']['hits']
        list=[]
        for line in query_scroll:
            list.append(line['_source'])
        yield list


def save(dic):
    #判别微博类型，实现微博的评论数和转发数的增加

    if dic['message_type'] == 1:
        #原创微博加入集合
        p = redis_ep.pipeline()
        p.sadd('Original_mid',dic['mid'])
        p.zadd(name='Originalmid_hot',mapping={dic['mid']:0})
        p.set(name=(dic['mid'] + 'comment'), value=0)
        p.set(name=(dic['mid'] + 'retweeted'),value=0)
        p.execute()
        print(dic['mid'])
    elif dic['message_type'] == 2:
        # 转发微博按照root_mid增加midcomment数
        if redis_ep.sismember(name='Original_mid',value= dic['root_mid']):
            redis_ep.set(name=(dic['root_mid'] + 'comment'),value=int(redis_ep.get(dic['root_mid'] + 'comment')) + 1)
            redis_ep.zincrby(name='Originalmid_hot',value=dic['root_mid'],amount=1)
            print(redis_ep.get(name=dic['root_mid'] + 'comment'))
    elif dic['message_type'] == 3:
        # 评论微博按照root_mid增加midretweeted数
        if redis_ep.sismember('Original_mid', dic['root_mid']):
            redis_ep.set(name = (dic['root_mid'] + 'retweeted'),value= int(r.get(dic['root_mid'] + 'retweeted')) + 1)
            redis_ep.zincrby(name='Originalmid_hot', value=dic['root_mid'], amount=1)
            print(redis_ep.get(name=dic['root_mid'] + 'retweeted'))



def put(q):
    #向队列中存入数据
    for list in data_query():
        for line in list:
            q.put(line)
        # print(q.qsize())
        time.sleep(round(random.uniform(0, 0.6), 3))
    end_time = time.time()
    print(end_time-start_time)


def is_political(message):
    #模拟判断是否是政治相关微博
    return message


def redis_save(q):
    #将政治相关的微博存入redis数据库中
    while True:
        # print(q.qsize())
        message = q.get()
        politicalmessage = is_political(message)
        save(politicalmessage)


def main():
    #用Queue实现子进程的通讯
    q = multiprocessing.Manager().Queue()
    # 利用多个进程模拟数据流的实时到达以及实时处理
    processings = []
    processings.append(multiprocessing.Process(target=put,args=(q,)))
    processings.append(multiprocessing.Process(target=redis_save, args=(q,)))
    processings.append(multiprocessing.Process(target=redis_save, args=(q,)))
    processings.append(multiprocessing.Process(target=redis_save, args=(q,)))
    processings.append(multiprocessing.Process(target=redis_save, args=(q,)))
    processings.append(multiprocessing.Process(target=redis_save, args=(q,)))
    processings.append(multiprocessing.Process(target=redis_save, args=(q,)))
    processings.append(multiprocessing.Process(target=redis_save, args=(q,)))
    processings.append(multiprocessing.Process(target=redis_save, args=(q,)))
    processings.append(multiprocessing.Process(target=redis_save, args=(q,)))
    processings.append(multiprocessing.Process(target=redis_save, args=(q,)))

    for i in processings:
        i.start()
    for i in processings:
        i.join()


if __name__ == '__main__':
   main()


