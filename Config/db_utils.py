from Config.base import *
from elasticsearch import Elasticsearch
import redis
import pymysql
from DBUtils.PooledDB import PooledDB


es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)

ees = Elasticsearch(hosts=[{'host': EES_HOST, 'port': EES_PORT}], timeout=1000)

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

def db_connect():
    es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)
    db = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db='PoliticalInfiltration',
        charset=DB_CHARSET
    )
    return es,db

def get_global_para(para_name):
    cursor = pi_cur()
    sql = "select p_value from GlobalParameter where p_name = '{}'".format(para_name)
    cursor.execute(sql)
    result = cursor.fetchone()
    return float(result["p_value"])

def get_event_para(e_id, para_name):
    cursor = pi_cur()
    sql = "select p_value from EventParameter where e_id = '{}' and p_name = '{}'".format(e_id, para_name)
    cursor.execute(sql)
    result = cursor.fetchone()
    return float(result["p_value"])

def get_global_senwords(contain_change=False):
    cursor = pi_cur()
    if contain_change:
        sql = "SELECT prototype, transform FROM SensitiveWord WHERE perspective_bias = 0"
        cursor.execute(sql)
        result = cursor.fetchall()
        prototype = [item["prototype"] for item in result]
        transform = [item["transform"] for item in result]
        result = list(set(prototype)) + transform
    else:
        sql = "SELECT prototype FROM SensitiveWord WHERE perspective_bias = 0 GROUP BY prototype"
        cursor.execute(sql)
        result = cursor.fetchall()
        result = [item["prototype"] for item in result]
    return result

def get_event_senwords(e_id, perspective=2):  # 1为白名单，2为黑名单
    cursor = pi_cur()
    sql = "SELECT prototype FROM SensitiveWord WHERE perspective_bias = {} AND e_id = '{}'".format(perspective, e_id)
    cursor.execute(sql)
    result = cursor.fetchall()
    result = [item["prototype"] for item in result]
    return result