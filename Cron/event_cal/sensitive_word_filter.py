import sys
sys.path.append("../../")
from Cron.event_cal.new_dfa import *
from Config.db_utils import es,conn,pi_cur
from Config.time_utils import *
from Cron.event_cal.data_utils import get_event_info
import re
# 创建一个dfa对象


def is_sexsitive_word(word,text):
    r = re.compile("([^0-9^a-z^A-Z])"+word+"([^0-9^a-z^A-Z])")
    rr  =r.findall(text)
    # print(r.match(text))
    if len(rr)!=0:
        return True
    else:
        return False

def querry(e_index,start_es,end_es):
    querrybody = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "timestamp": {
                                "gt": start_es,
                                "lt": end_es
                            }
                        }
                    },
                ],
                "must_not": [],
                "should": []
            }
        },
        "from": 0,
        "sort": [],
        "aggs": {}
    }
    query = es.search(index=e_index, body=querrybody, scroll='5m', size=10000)

    results = query['hits']['hits']  # es查询出的结果第一页
    total = query['hits']['total']  # es查询出的结果总量
    scroll_id = query['_scroll_id']  # 游标用于输出es查询出的所有结果
    list = []
    for line in results:
        list.append(line['_source'])
    for i in range(0, int(total / 10000) + 1):
        # scroll参数必须指定否则会报错
        query_scroll = es.scroll(scroll_id=scroll_id, scroll='5m')['hits']['hits']

        for line in query_scroll:
            list.append(line['_source'])
        yield list

def get_notsensitive_word(e_id):
    cusor = pi_cur()
    sql = "select prototype from SensitiveWord where e_id = '{}' and perspective_bias = 1".format(e_id)
    cusor.execute(sql)
    results = cusor.fetchall()
    with open('not_sensitive_word.txt','w',encoding='utf-8') as wf:
        for result in results:
            wf.write(result['prototype']+'\n')

def sensitive_word_filter(n,e_id):
    get_notsensitive_word(e_id)
    dfa = DFA()
    dfa.change_words('not_sensitive_word.txt')
    key_words, start_date, end_date, e_index = get_event_info(e_id)
    if n==0:
        start_ts = date2ts(str(start_date))
        if end_date == None:
            end_ts = time.time()
        else:
            end_ts = date2ts(str(end_date))
    else:
        end_ts = int(time.mktime(datetime.date.today().timetuple()))
        start_ts = end_ts-86400
    data_dict = {}
    for data_list in querry(e_index,start_ts,end_ts):
        for message in data_list:
            if not dfa.exists(message['text']):
                data_dict[message['mid']] = {}
                data_dict[message['mid']]['uid'] = message['uid']
                data_dict[message['mid']]['text'] = message['text']
                data_dict[message['mid']]['root_uid'] = message['root_uid']
                data_dict[message['mid']]['root_mid'] = message['root_mid']
                data_dict[message['mid']]['timestamp'] = message['timestamp']
                data_dict[message['mid']]['send_ip'] = message['ip']
                data_dict[message['mid']]['geo'] = message['geo']
                data_dict[message['mid']]['message_type'] = message['message_type']
                data_dict[message['mid']]['source'] = message['source']

    return data_dict