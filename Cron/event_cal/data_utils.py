import sys
import elasticsearch.helpers
sys.path.append("../../")
from Config.db_utils import es, ees, pi_cur, conn
from Cron.event_cal.SentimentalPolarities import sentiment_polarities
from Config.time_utils import *
from collections import defaultdict                                   


def get_edic_daily():
    cursor = pi_cur()
    sql = 'select * from Event where monitor_status = 1 and cal_status = 2'
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def get_edic_add():
    cursor = pi_cur()
    sql = 'select * from Event where monitor_status = 1 and cal_status = 0'
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


# 向mysql数据库一次存入多条数据，数据输入为data_dict 格式{id1:{item1},id2:{item2},}
def sql_insert_many(table_name, primary_key, data_dict):
    cursor = pi_cur()
    columns = []
    params = []
    columns.append(primary_key)
    for item_id in data_dict:
        item = data_dict[item_id]
        param_one = []
        param_one.append(item_id)
        for k, v in item.items():
            if k not in columns:
                columns.append(k)
            param_one.append(v)
        params.append(tuple(param_one))
    columns_sql = ",".join(columns)
    values = []
    for i in range(len(columns)):
        values.append("%s")
    values_sql = ",".join(values)
    sql = 'replace into %s (%s) values (%s)' % (table_name, columns_sql, values_sql)

    if len(params):
        n = cursor.executemany(sql, params)
        m = len(params)
        print("insert {} success, {} failed".format(m, m - n))
        conn.commit()
    else:  
        print('empty data')






def get_event_info(e_id):
    sql = "select keywords_dict,begin_date,end_date,es_index_name from Event where e_id = '{}'".format(e_id)
    cursor = pi_cur()
    cursor.execute(sql)
    results = cursor.fetchall()[0]
    return results['keywords_dict'],results['begin_date'],results['end_date'],results['es_index_name']

def getEveryDay(begin_date,end_date):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date,"%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list

def search_es(index,keywords):
    query_body = {
        "query":{
            "match_phrase":{
                'text':keywords
            },
     }
    }
    query = es.search(index=index,body=query_body,scroll='5m',size = 10000)

    results = query['hits']['hits'] # es查询出的结果第一页
    total = query['hits']['total']  # es查询出的结果总量
    scroll_id = query['_scroll_id'] # 游标用于输出es查询出的所有结果

    list = []
    for line in results:
        list.append(line['_source'])
    yield list


    for i in range(0, int(total/10000)+1):
        # scroll参数必须指定否则会报错
        query_scroll = es.scroll(scroll_id=scroll_id,scroll='5m')['hits']['hits']
        list=[]
        for line in query_scroll:
            list.append(line['_source'])
        yield list


def event_es_save(save,e_index):
    actions = [
        {
            '_op_type': 'index',
            '_index': e_index,
            '_type': "event_weibo",
            '_source': d,
            '_id': d['mid']
        }
        for d in save
    ]
    elasticsearch.helpers.bulk(ees, actions=actions)


def create_event_index(e_index):
    event_data = {
        'settings': {
            'number_of_replicas': 0,
            'number_of_shards': 5,
            },
        'mappings': {
            'event_weibo': {
                'properties': {
                    'source': {
                        'type': 'keyword',
                        'index':True
                    },
                    'uid': {
                        'type': 'keyword',
                        'index': True
                    },
                    'root_uid': {
                        'type': 'keyword',
                        'index': True
                    },
                    'mid': {
                        'type': 'keyword',
                        'index': True
                    },
                    'root_mid': {
                        'type': 'keyword',
                        'index': True
                    },
                    'message_type': {
                        "type": "byte",
                        'index':True
                    },
                    'sentiment_polarity': {
                        'type': 'byte',
                    },
                    'text': {
                        'type': 'text',
                        "analyzer": "ik_max_word"
                    },
                    'geo': {
                        'type': 'keyword',
                    },
                    'net_type': {
                        'type': 'text',
                        'index':True,
                    },
                    'user_fansnum': {
                        'type': 'integer',
                    },
                    'timestamp': {
                        'type': 'long',
                    },
                    'rootid_retweetnum': {
                        'type': 'integer',
                    },
                    'mobile_type': {
                        'type': 'integer',
                    },
                    'client_type': {
                        'type': 'keyword',
                    },
                    'audit_status': {
                        'type': 'integer',
                    },
                    'send_srcport': {
                        'type': 'integer',
                    },
                    'video_url': {
                        'type': 'keyword',
                    },
                    'rootid_commentnum': {
                        'type':  'integer',
                    },
                    'user_friendsnum': {
                        'type':  'integer',
                    },
                    'sp_type': {
                        'type': 'integer',
                    },
                    'audio_content': {
                        'type': 'keyword',
                    },
                    'pic_content': {
                        'type': 'keyword',
                    },
                    'retweeted': {
                        'type':'integer',
                    },
                    'comment': {
                        'type': 'integer',
                    },
                    'video_content': {
                        'type': 'keyword',
                    },
                    'audio_url': {
                        'type': 'keyword',
                    },
                    'client_remark': {
                        'type': 'keyword',
                    },
                    'pic_url': {
                        'type': 'keyword',
                    },
                    'ip': {
                        'type': 'keyword',
                    },
                }
            },
        }
    }
    result = ees.indices.create(index=e_index, ignore=400, body=event_data)
    print(result)


def save_event_data(e_id, n, SENTIMENT_POS, SENTIMENT_NEG):

    if n==0:
        key_words,start_date,end_date,e_index = get_event_info(e_id)
        # if datetime.datetime.strptime(str(start_date), "%Y-%m-%d")<datetime.datetime.strptime(str(datetime.datetime.today() - datetime.timedelta(days=20))[:10],"%Y-%m-%d"):
        #     start_date = datetime.datetime.strptime(str(datetime.datetime.today() - datetime.timedelta(days=20))[:10],"%Y-%m-%d")
        key_words_list = key_words.split('、')
        if end_date == None:
            end_date = datetime.datetime.today()
        date_list = getEveryDay(str(start_date)[:10],str(end_date)[:10])
        indexes = ['flow_text_'+ date for date in date_list]
    else:
        key_words, start_date, end_date, e_index = get_event_info(e_id)
        key_words_list = key_words.split('、')
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        yesterday = today - oneday
        indexes = ['flow_text_' + str(yesterday)]
    for index in indexes:
        messages = []
        data_dict = {}
        for keyword in key_words_list:
            for data_list in search_es(index,keyword):
                for message in data_list:
                    messages.append(message)
                    data_dict[message['mid']]=message['text']
            sentiment_dict = sentiment_polarities(data_dict, SENTIMENT_POS, SENTIMENT_NEG)
            save = []
            for message in messages:
                message['sentiment_polarity'] = sentiment_dict[message['mid']]
                message['source'] = '新浪'
                save.append(message)
            if ees.indices.exists(index=e_index):
                event_es_save(save,e_index)
            else:
                create_event_index(e_index)
                event_es_save(save, e_index)



# 敏感信息入库
def sensitivity_store(data_dict):
    if len(data_dict) == 0:
        print('no data')
    else:
        cursor = pi_cur()
        sql = 'replace into Information set i_id=%s,uid=%s,root_uid=%s,mid=%s,text=%s,timestamp=%s,' \
              'send_ip=%s,geo=%s,message_type=%s,root_mid=%s,source=%s,monitor_status=1,hazard_index=NULL,' \
              'cal_status=0,add_manully=0'
        val = []
        for i, j in data_dict.items():
            val.append((j.get('source',None)+i,j.get('uid',None),j.get('root_uid',None),i,j.get('text',None),
                        j.get('timestamp',None),j.get('send_ip',None),j.get('geo',None),
                        j.get('message_type',None),j.get('root_mid',None),j.get('source',None)))
        # 执行sql语句
        n = cursor.executemany(sql, val)
        print("入库成功 %d 条" % n)
        conn.commit()


# 敏感信息和事件关联入库
def event_sensitivity(e_id,data_dict):
    if len(data_dict) == 0:
        print('no data')
    else:
        cursor = pi_cur()
        sql = 'insert into Event_information set event_id=%s,information_id=%s'
        val = []
        for i in data_dict:
            val.append((e_id,i))
        # 执行sql语句
        n = cursor.executemany(sql, val)
        print("入库成功 %d 条" % n)
        conn.commit()


# 事件计算时获取数据
def get_event_data(e_index, start_date, end_date):
    start_ts = date2ts(str(start_date))
    if end_date == None:
        end_ts = time.time()
    else:
        end_ts = date2ts(str(end_date)) + 86400

    query_body = {
        "query": {
            "bool": {
                "must": [
                    {"range": {"timestamp": {"gte": start_ts, "lt": end_ts}}},
                ]
            }
        }
    }

    result = elasticsearch.helpers.scan(ees, index=e_index, query=query_body)

    data = defaultdict(list)
    for item in result:
        item = item["_source"]
        date = ts2date(item["timestamp"])                        
        data[date].append(item)
    return data


# 初始化新事件参数
def store_event_para(e_id, p_name):
    cursor = pi_cur()
    sql = 'replace into EventParameter values (%s, %s, %s, %s, %s)'
    parameters = {'sentiment_neg':(e_id+'sentiment_neg','sentiment_neg',0.2,e_id,'信息情感极性负面阈值'),
    'sentiment_pos':(e_id+'sentiment_pos','sentiment_pos',0.7,e_id,'信息情感极性正面阈值'),
    'pos_num':(e_id+'pos_num','pos_num',1000,e_id,'敏感计算时正类数量'),
    'neg_num':(e_id+'neg_num','neg_num',15000,e_id,'敏感计算时负类数量'),
    'weibo_num':(e_id+'weibo_num','weibo_num',100000,e_id,'每日LDA聚类时采样的微博总数')}
    cursor.executemany(sql, [parameters[p_name]])
    conn.commit()
