#-*-coding=utf-8-*-
import sys
import os
import time
import datetime
import json
import pymysql
from elasticsearch.helpers import scan
from collections import defaultdict
sys.path.append("../")
from profile_cal.data_get_utils import sql_insert_many

sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'

from Config.db_utils import es, pi_cur, conn

cursor = pi_cur()



def event_analyze(index_name,e_id):
    #end_time = int(time.mktime(datetime.date.today().timetuple()))
    #start_time = end_time - 24 * 60 * 60
    data_dict = defaultdict(list)
    sdata_dict = defaultdict(list)
    idata_dict = defaultdict(list)
    analyze_dict = {}
    all_dict = {}
    sensitive_dict = {}
    negative_dict = {}
    '''
    sql = 'select Information.timestamp,Information.i_id from Event_information ei \
            left join Information on ei.information_id = Information.i_id \
            where ei.event_id = %s' % (e_id)
    cursor.execute(sql)
    '''
    cursor.execute('select Information.timestamp,Information.i_id from Event_information ei \
            left join Information on ei.information_id = Information.i_id \
            where ei.event_id = %s',e_id)
    result = cursor.fetchall()
    for re in result:
        #print(re)
        lt = time.localtime(re['timestamp'])
        day = time.strftime('%Y-%m-%d',lt)
        idata_dict[day].append(re['i_id'])
    query_body = {
        "query": {
        "match_all":{}
        }
    }
    if index_name ==" ":
        index_name = "weibo_all"
    r = scan(es, index=index_name, query=query_body)
    weibo_count = 0
    user_list =[]
    user_count = 0
    for item in r:
        weibo_count += 1
        day = item['_source']["time"][0:10]
        if day == " ":
            continue
        else:
            data_dict[day].append(item['_source'])
            if int(item['_source']["sentiment"])<0:
                sdata_dict[day].append(item['_source'])
        if item['_source']["uid"] in user_list:
            continue
        else:
            user_count += 1
            user_list.append(item['_source']["uid"])
    thedate = datetime.date.today()
    for k in data_dict.keys():
        all_dict[k] = len(data_dict[k])
        if k not in sdata_dict.keys():
            negative_dict[k] = 0
        else:
            negative_dict[k] = len(sdata_dict[k])
        if k not in idata_dict.keys():
            sensitive_dict[k] = 0
        else:
            sensitive_dict[k] = len(idata_dict[k])
    all_json = json.dumps(all_dict)
    sensitive_json = json.dumps(sensitive_dict)
    negative_json = json.dumps(negative_dict)
    '''
    sql = 'insert into Event_analyze values (%s,%s,%s,%s,%s,%s)' % (e_id,e_id,all_json,sensitive_json,negative_json,thedate)
    #sql = 'insert into Event_analyze values (%s,%s,%s,%s,%s,%s)' % (e_id,e_id,pymysql.escape_string(all_json),pymysql.escape_string(sensitive_json),pymysql.escape_string(negative_json),thedate)
    cursor.execute(sql)#'insert into Event_Analyze(e_id,event_name,hot_index,sensitive_index,negative_index,into_date) values ("{}","{}","{}","{}","{}","{}")'.format(e_id,e_id,all_json,sensitive_json,negative_json,thedate))
    conn.commit()
    '''
    analyze_dict[e_id] = {"event_name":e_id,
                            "hot_index":all_json,
                            "sensitive_index":sensitive_json,
                            "negative_index":negative_json,
                            "user_count":user_count,
                            "weibo_count":weibo_count,
                            "into_date":thedate}
    sql_insert_many(cursor, "Event_Analyze", "e_id", analyze_dict)
'''
    query_body1 = {
        "query": {
            "bool": {
                "filter": [
                    {"range":
                    {"sentiment": 
                    {"lte": 0
                                }
                                }
                                }
                            ]
                        }
                    }
        }
    r1 = scan(es, index='weibo_user', query=query_body1)

'''
if __name__ == '__main__':
    #thedate = datetime.date.today()
    '''
    sql = 'select e_id,es_index_name from Event'
    cursor.execute(sql)
    result = cursor.fetchall()
    for re in result:
        event_analyze(re['es_index_name'],re['e_id'])
        '''
    eid = 'xianggangshijian_1581919160'
    event_analyze("weibo_all",eid)