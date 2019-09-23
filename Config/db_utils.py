from Config.base import *
from elasticsearch import Elasticsearch
import redis
import pymysql
from DBUtils.PooledDB import PooledDB


es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)

redis_ep = redis.Redis(connection_pool=redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0))

pi_pool = PooledDB(creator=pymysql,mincached=DB_MIN_CACHED,
    maxcached=DB_MAX_CACHED,maxconnections=DB_MAX_CONNECYIONS,
    host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
    db='PoliticalInfiltration',charset=DB_CHARSET, cursorclass=pymysql.cursors.DictCursor)
conn = pi_pool.connection()

def pi_cur():
    conn.ping(reconnect=True)
    return conn.cursor()

def test_sample(table):
    cur = conn.cursor()
    sql = 'select * from %s' % table
    cur.execute(sql)
    data = cur.fetchone()
    cur.close()
    return data