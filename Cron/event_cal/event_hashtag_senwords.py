import re
import sys
import json
sys.path.append("../../")

from Config.db_utils import es, pi_cur, conn
from Config.time_utils import *
from Cron.event_cal.data_utils import sql_insert_many

# 统计事件在一段时间内的微博信息
def event_hashtag_senwords(e_id, data_dict, n):
    # 正则规则构建，包括全局敏感词、事件敏感词、hashtag
    global_senwords_list = []
    with open('sensitive_words_list_add.txt','r',encoding='utf-8') as f:
        for l in  f.readlines():
            global_senwords_list.append(l.strip())

    event_senwords_list = []
    with open('高精度敏感词.txt','r',encoding='utf-8') as f:
        for l in  f.readlines():
            event_senwords_list.append(l.strip())

    re_global_senwords = re.compile('|'.join(global_senwords_list))
    re_event_senwords = re.compile('|'.join(event_senwords_list))

    re_hashtag = re.compile('#.+?#')

    # 遍历日期进行数据计算，统计敏感词和hashtag的出现频率
    hashtag_dic = {}
    global_senwords_dic = {}
    event_senwords_dic = {}
    for date in sorted(list(data_dict.keys())):
        print(date, len(data_dict[date]))
        hashtag_dic[date] = {}
        global_senwords_dic[date] = {}
        event_senwords_dic[date] = {}

        for text in data_dict[date]:
            text = text['text']
            for hashtag in re_hashtag.findall(text):
                if hashtag in hashtag_dic[date]:
                    hashtag_dic[date][hashtag] += 1
                else:
                    hashtag_dic[date][hashtag] = 1

            if global_senwords_list:
                for global_senword in re_global_senwords.findall(text):
                    if global_senword in global_senwords_dic[date]:
                        global_senwords_dic[date][global_senword] += 1
                    else:
                        global_senwords_dic[date][global_senword] = 1

            if event_senwords_list:
                for event_senword in re_event_senwords.findall(text):
                    if event_senword in event_senwords_dic[date]:
                        event_senwords_dic[date][event_senword] += 1
                    else:
                        event_senwords_dic[date][event_senword] = 1

    # 统计后数据批量插入数据库
    insert_dic = {}
    for date in sorted(list(hashtag_dic.keys())):
        timestamp = date2ts(date)
        ehs_id = "{}_{}".format(str(timestamp), e_id)
        hashtag = json.dumps(hashtag_dic[date])
        global_senword = json.dumps(global_senwords_dic[date])
        event_senword = json.dumps(event_senwords_dic[date])

        insert_dic[ehs_id] = {
            "e_id": e_id,
            "hashtag": hashtag,
            "global_senword": global_senword,
            "event_senword": event_senword,
            "timestamp": timestamp,
            "into_date": date,
            "show_status": 0
        }
    sql_insert_many("Event_Hashtag_Senwords", "ehs_id", insert_dic)

    # 对事件所有的统计结果进行统计，更新至展示数据表
    # 新事件计算时，把所有计算好的结果直接统计进入最后一天的表
    if n == 0:
        update_show_data(hashtag_dic, global_senwords_dic, event_senwords_dic, e_id, date)
    # 每日更新时，取出最后更新的日期与当前计算日期之间的所有数据，与原更新日期进行合并统计
    elif n == 1:
        # 取出历史计算的记录，将内容和日期添加至计算字典内
        sql_all = "SELECT * from Event_Hashtag_Senwords where ehs_id = '{}'".format(e_id)
        cursor = pi_cur()
        cursor.execute(sql_all)
        result = cursor.fetchone()
        show_date = result["into_date"].strftime('%Y-%m-%d')
        hashtag_dic[show_date] = json.loads(result["hashtag"])
        global_senwords_dic[show_date] = json.loads(result["global_senword"])
        event_senwords_dic[show_date] = json.loads(result["event_senword"])

        # 取出中间未统计过的记录，将内容和日期添加至计算字典内
        sql_add = "SELECT * from Event_Hashtag_Senwords where e_id = '{}' and timestamp > {} and timestamp < {}".format(e_id, date2ts(show_date), date2ts(date))
        cursor.execute(sql_add)
        result = cursor.fetchall()
        for item in result:
            item_date = item["into_date"].strftime('%Y-%m-%d')
            hashtag_dic[item_date] = json.loads(item["hashtag"])
            global_senwords_dic[item_date] = json.loads(item["global_senword"])
            event_senwords_dic[item_date] = json.loads(item["event_senword"])

        update_show_data(hashtag_dic, global_senwords_dic, event_senwords_dic, e_id, date)

# 将所有日期的对应字典就行统计，存储在一条记录中以方便取用
def update_show_data(hashtag_dic, global_senwords_dic, event_senwords_dic, e_id, sta_date):
    hashtag_dic_all = {}
    global_senwords_dic_all = {}
    event_senwords_dic_all = {}

    for date in hashtag_dic:
        for hashtag in hashtag_dic[date]:
            if hashtag in hashtag_dic_all:
                hashtag_dic_all[hashtag] += hashtag_dic[date][hashtag]
            else:
                hashtag_dic_all[hashtag] = hashtag_dic[date][hashtag]

        for global_senword in global_senwords_dic[date]:
            if global_senword in global_senwords_dic_all:
                global_senwords_dic_all[global_senword] += global_senwords_dic[date][global_senword]
            else:
                global_senwords_dic_all[global_senword] = global_senwords_dic[date][global_senword]

        for event_senword in event_senwords_dic[date]:
            if event_senword in event_senwords_dic_all:
                event_senwords_dic_all[event_senword] += event_senwords_dic[date][event_senword]
            else:
                event_senwords_dic_all[event_senword] = event_senwords_dic[date][event_senword]

    insert_dic = {}
    timestamp = date2ts(sta_date)
    ehs_id = e_id
    hashtag = json.dumps(hashtag_dic_all)
    global_senword = json.dumps(global_senwords_dic_all)
    event_senword = json.dumps(event_senwords_dic_all)
    insert_dic[ehs_id] = {
            "e_id": e_id,
            "hashtag": hashtag,
            "global_senword": global_senword,
            "event_senword": event_senword,
            "timestamp": timestamp,
            "into_date": sta_date,
            "show_status": 1
        }
    sql_insert_many("Event_Hashtag_Senwords", "ehs_id", insert_dic)