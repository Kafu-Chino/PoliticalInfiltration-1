from elasticsearch import Elasticsearch
import redis

ES_HOST = '219.224.134.214'
ES_PORT = 9211

REDIS_HOST = '219.224.134.214'
REDIS_PORT = 6666

es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)
redis_ep = redis.Redis(connection_pool=redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0))