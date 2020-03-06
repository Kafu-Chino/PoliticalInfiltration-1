import sys
sys.path.append("../../")

from copy import deepcopy
from collections import defaultdict

from Config.db_utils import es, pi_cur, conn, get_global_para
from Config.time_utils import *
from Cron.information_cal.data_utils import sql_insert_many

basic_fraction = get_global_para("information_basic_fraction")
max_count = get_global_para("information_trend_max_count")
decay_ratio = get_global_para("information_trend_decay_ratio")

def get_trend(mid_dic, start_date, end_date):
    # 初始搜索列表的构建，原创微博为自身，转发评论微博为其原创微博
    search_dic = defaultdict(list)
    message_type_dic = {}
    for item in mid_dic:
        if item["message_type"] == 1:
            search_dic[item['mid']].append(item['mid'])
        else:
            search_dic[item['root_mid']].append(item['mid'])
        message_type_dic[item['mid']] = item["message_type"]
    search_list = list(search_dic.keys())
    
    # es聚合主体，对每日的被查询mid的被转发和被评论（即作为root_mid）进行聚合
    query_body = {
        "query": {
            "terms": {
                "root_mid": search_list
            }
        },
        "aggs": {
            "count": {
                "terms": {
                    "field": "root_mid",
                    "size": len(search_list)
                },
                "aggs": {
                    "message_type": {
                        "terms": {
                            "field": "message_type"
                        }
                    }
                }
            }
        },
        "size": 0
    }

    ''' 对聚合结果进行计数，结果字典为
    {
        "date":{
            "mid":{
                'comment_count': comment_count,
                'retweet_count': retweet_count,
            }
        }
    }
    存在可能，多个微博可能具有同一个查询微博mid，即可能有几条敏感信息都转发或评论了同一原创微博，且可能该原创微博自身也为敏感微博。
    '''
    result_dic = defaultdict(dict)
    for date in get_datelist_v2(start_date, end_date):
        query_body["query"] = {
            "bool":{
                "must": [
                    {"terms": {"root_mid": search_list}},
                    {"range": {"timestamp": {"gte": date2ts(date), "lt": date2ts(date) + 86400}}}
                ]
            }
        }
        res = es.search(index='flow_text_{}'.format(date), body=query_body)
        # res = es.search(index='weibo_all', body=query_body)

        sta_res = res["aggregations"]["count"]["buckets"]
        for item in sta_res:
            comment_count = 0
            retweet_count = 0

            for count_item in item["message_type"]["buckets"]:
                if count_item["key"] == 2:
                    comment_count = count_item["doc_count"]
                if count_item["key"] == 3:
                    retweet_count = count_item["doc_count"]

            search_mid = item["key"]
            for mid in search_dic[search_mid]:
                result_dic[date][mid] = {
                    'comment_count': comment_count,
                    'retweet_count': retweet_count,
                }

    # 将统计的结果存入数据库中
    insert_dic = {}
    for date in result_dic:
        for mid in result_dic[date]:
            is_id = "{}_{}".format(date2ts(date), mid)
            insert_dic[is_id] = {
                "mid": mid,
                "comment_count": result_dic[date][mid]["comment_count"],
                "retweet_count": result_dic[date][mid]["retweet_count"], 
                "timestamp": date2ts(date),
                "hazard_index": 50,
                "store_date": date,
                "message_type": message_type_dic[mid]
            }
    sql_insert_many("Informationspread", "is_id", insert_dic)


    # 计算危害指数并更新
    hazard_index_dic = cal_hazard_index(mid_dic, insert_dic, start_date, end_date)


def cal_hazard_index(mid_dic, insert_dic, start_date, end_date):
    cursor = pi_cur()
    mid_type = {item["mid"]: item["message_type"] for item in mid_dic}
    mid_list = [item["mid"] for item in mid_dic]

    hazard_index_dic = defaultdict(dict)
    # 对过去30天的结果进行聚合
    for date in get_datelist_v2(start_date, end_date):
        agg_sql = "SELECT sum(comment_count), sum(retweet_count), mid from Informationspread WHERE `timestamp` >= {} and `timestamp` <= {} and mid in ('{}') GROUP BY mid".format(date2ts(date) - 30 * 86400, date2ts(date), "','".join(mid_list))
        cursor.execute(agg_sql)
        result = cursor.fetchall()

        for item in result:
            mid = item["mid"]
            count = item["sum(comment_count)"] + item["sum(retweet_count)"]
            # 危害指数的计算公式
            basic_decay = 100 - basic_fraction
            if mid_type[mid] == 1:
                hazard_index = float(count) * basic_decay / max_count + basic_fraction
            else:
                hazard_index = float(count) * basic_decay * decay_ratio / max_count + basic_fraction
            if hazard_index > 100:
                hazard_index = 100
            hazard_index_dic[date][mid] = hazard_index

    # 构建更新数据格式
    update_dic = {}
    update_dic_information = {}
    for date in get_datelist_v2(start_date, end_date):
        for mid in mid_type:
            is_id = "{}_{}".format(date2ts(date), mid)
            if is_id not in insert_dic:
                continue
            update_dic[is_id] = {
                "hazard_index": hazard_index_dic[date][mid]
            }
            update_dic_information[mid] = {
                "hazard_index": hazard_index_dic[date][mid]
            }

    # 更新至信息态势库
    sql = "UPDATE Informationspread SET hazard_index = %s WHERE is_id = %s"

    params = [(update_dic[is_id]["hazard_index"], is_id) for is_id in update_dic]
    n = cursor.executemany(sql, params)
    conn.commit()

    # 更新至信息库，无数据的置为初始值
    for item in mid_dic:
        if item["mid"] in update_dic_information:
            update_dic_information[item["i_id"]] = update_dic_information.pop(item["mid"])
        else:
            update_dic_information[item["i_id"]] = {
                "hazard_index": basic_fraction
            }

    sql = "UPDATE Information SET hazard_index = %s WHERE i_id = %s"

    params = [(update_dic_information[i_id]["hazard_index"], i_id) for i_id in update_dic_information]
    n = cursor.executemany(sql, params)
    conn.commit()