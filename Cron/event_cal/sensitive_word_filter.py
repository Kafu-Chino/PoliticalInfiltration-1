import sys
sys.path.append("../../")
from Cron.event_cal.new_dfa import *
from Config.db_utils import ees,conn,pi_cur
from Config.time_utils import *
from Cron.event_cal.data_utils import get_event_info
from Cron.event_cal.data_utils import sensitivity_store,event_sensitivity
from Cron.event_cal.event_semantic import Weibo_utils
from Cron.event_cal.figure_add import figure_add
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
                                "gte": start_es,
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
    query = ees.search(index=e_index, body=querrybody, scroll='5m', size=10000)

    results = query['hits']['hits']  # es查询出的结果第一页
    total = query['hits']['total']  # es查询出的结果总量
    scroll_id = query['_scroll_id']  # 游标用于输出es查询出的所有结果
    list = []
    for line in results:
        list.append(line['_source'])
    yield list
    for i in range(0, int(total / 10000) + 1):
        # scroll参数必须指定否则会报错
        query_scroll = ees.scroll(scroll_id=scroll_id, scroll='5m')['hits']['hits']
        list = []
        for line in query_scroll:
            list.append(line['_source'])
        yield list

def get_sensitive_word(e_id,bias,file):
    cusor = pi_cur()
    sql = "select prototype from SensitiveWord where e_id = '{}' and perspective_bias = '{}'".format(e_id,bias)
    cusor.execute(sql)
    results = cusor.fetchall()
    with open(file,'w',encoding='utf-8') as wf:
        for result in results:
            wf.write(result['prototype']+'\n')

def sensitive_word_filter(n,e_id):
    get_sensitive_word(e_id,1,'not_sensitive_word.txt')
    dfa = DFA()
    weibo_utils = Weibo_utils()
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
    num = 0
    for data_list in querry(e_index,start_ts,end_ts):
        num += 1
        print(num)
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
    new_data_dict = {}
    save_data_dict = {}
    get_sensitive_word(e_id, 2, 'sensitive_word.txt')
    dfa.change_words('sensitive_word.txt')
    for mid in data_dict.keys():
        text = weibo_utils.remove_nochn(weibo_utils.remove_c_t(data_dict[mid]['text']))
        if dfa.exists(text):
            line = dfa.filter_all(text)
            line_list = line.split('\t')
            new_line = line_list[0]
            if len(line_list) != 1:
                for i in range(1, len(line_list)):
                    if is_sexsitive_word(line_list[i], line_list[0]):
                        save_data_dict[mid] = data_dict[mid]
                    else:
                        new_data_dict[mid] = data_dict[mid]
            else:
                new_data_dict[mid] = data_dict[mid]
        else:
            new_data_dict[mid] = data_dict[mid]
    sensitivity_store(save_data_dict)
    event_sensitivity(e_id,save_data_dict)
    figure_add(save_data_dict,e_id)
    return new_data_dict
if __name__ == '__main__':
    sensitive_word_filter(0,'xianggangshijian_1581919160')