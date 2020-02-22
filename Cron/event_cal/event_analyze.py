#-*-coding=utf-8-*-
import sys
import os
import time
import datetime
import json
import pymysql
from elasticsearch.helpers import scan
from collections import defaultdict
import re


sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'

from Config.db_utils import es, pi_cur, conn
from Cron.event_cal.data_utils import sql_insert_many
cursor = pi_cur()

#geo_list=['北京','天津','重庆','上海','河北','山西','辽宁','吉林','黑龙江','江苏','浙江','安徽','福建','江西','山东','河南','湖北','湖南','广东','海南','四川','贵州','云南','陕西','甘肃','青海','台湾','内蒙古','广西','西藏','宁夏','新疆','香港','澳门']
thedate = datetime.date.today()
def event_analyze(index_name,e_id,date=thedate):
    #end_time = int(time.mktime(datetime.date.today().timetuple()))
    #start_time = end_time - 24 * 60 * 60
    td = str(date) + " 00:00:00"
    data_dict = defaultdict(list)
    sdata_dict = defaultdict(list)
    idata_dict = defaultdict(list)
    analyze_dict = {}
    geo_dict = {}
    all_dict = {}
    out_dict={}
    in_dict = {}
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
    for res in result:
        #print(re)
        lt = time.localtime(res['timestamp'])
        day = time.strftime('%Y-%m-%d',lt)
        idata_dict[day].append(res['i_id'])
    query_body = {
        "query": {
        "bool": {
                "must": [
                    {"range": {"time": {"lt": td}}},
                ]
            }
        }
    }
    if index_name ==" ":
        index_name = "weibo_all"
    r = scan(es, index=index_name, query=query_body)
    weibo_count = 0
    user_list ={}
    user_count = 0
    pattern = re.compile(r'(\u4e2d\u56fd)')
    #pattern1 = re.compile(r'(\u9999\u6e2f|\u6fb3\u95e8|\u5b81\u590f|\u5e7f\u897f|\u65b0\u7586|\u897f\u85cf|\u5185\u8499\u53e4|\u9ed1\u9f99\u6c5f)')
    #pattern2 = re.compile(r'([\u4e00-\u9fa5]{2,5}?(\u7701|\u5e02|\u81ea\u6cbb\u533a))')  #\u7701省   \u5e02市     \u81ea\u6cbb\u533a自治区
    for item in r:
        weibo_count += 1
        day = item['_source']["time"][0:10]
        if day == " ":
            continue
        else:
            data_dict[day].append(item['_source'])
            if int(item['_source']["sentiment"])<0:
                sdata_dict[day].append(item['_source'])
        try:
            user_list[item['_source']["uid"]] = 1
        except:
            continue
        k = pattern.match(item['_source']["geo"])
        if k is None:
            try:
                out_dict[item['_source']["geo"]] += 1
            except:
                out_dict[item['_source']["geo"]] = 1
        else:
            try:
                in_dict[item['_source']["geo"]] += 1
            except:
                in_dict[item['_source']["geo"]] = 1
        '''
        #print(item['_source']["geo"])
        k1 = pattern1.match(item['_source']["geo"])
        if k1 is None:
            k2 = pattern2.match(item['_source']["geo"])
            if k2 is None:
                k3 = re.match(r'.+(\u7701)',item['_source']["geo"])
                if k3 is None:
                    try:
                        out_dict[item['_source']["geo"]] += 1
                    except:
                        out_dict[item['_source']["geo"]] = 1
                else:
                    #print(k3.group()[-3:])
                    try:
                        in_dict[k3.group()[-3:]] += 1
                    except:
                        in_dict[k3.group()[-3:]] = 1
            else:
                #print(k2.group())
                try:
                    in_dict[k2.group()] += 1
                except:
                    in_dict[k2.group()] = 1
        else:
            #print(k1.group())
            try:
                in_dict[k1.group()] += 1
            except:
                in_dict[k1.group()] = 1
            '''
    user_count = len(user_list.keys())
    #print(user_count,weibo_count)
    #thedate = datetime.date.today()
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
    in_json = json.dumps(in_dict)
    out_json = json.dumps(out_dict)
    #sql = 'insert into Event_analyze values (%s,%s,%s,%s,%s,%s)' % (e_id,e_id,all_json,sensitive_json,negative_json,thedate)
    #sql = 'insert into Event_analyze values (%s,%s,%s,%s,%s,%s)' % (e_id,e_id,pymysql.escape_string(all_json),pymysql.escape_string(sensitive_json),pymysql.escape_string(negative_json),thedate)
    #'insert into Event_Analyze(e_id,event_name,hot_index,sensitive_index,negative_index,into_date) values ("{}","{}","{}","{}","{}","{}")'.format(e_id,e_id,all_json,sensitive_json,negative_json,thedate))

    analyze_dict[e_id] = {"event_name":e_id,
                            "hot_index":all_json,
                            "sensitive_index":sensitive_json,
                            "negative_index":negative_json,
                            "geo_inland":in_json,
                            "geo_outland":out_json,
                            "user_count":user_count,
                            "weibo_count":weibo_count,
                            "into_date":date}
    sql_insert_many(cursor, "Event_Analyze", "e_id", analyze_dict)


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