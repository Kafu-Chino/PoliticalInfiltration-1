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
def event_analyze(e_id,data,date=thedate):
    end_time=datetime.datetime.strptime(date+ " 23:59:59", '%Y-%m-%d %H:%M:%S').timestamp()
    #end_time = int(time.mktime(date.timetuple()))
    start_time = end_time - 24 * 60 * 60
    #td = str(date) + " 23:59:59"
    #data_dict = defaultdict(list)
    #sdata_dict = defaultdict(list)
    #idata_dict = defaultdict(list)
    analyze_dict = {}
    geo_dict = {}
    out_dict={}
    in_dict = {}
    in_info_dict = {}
    out_info_dict = {}
    sensitive = 0
    negative = 0
    weibo_count = len(data)
    '''
    cursor.execute('select Information.timestamp,Information.i_id from Event_information ei \
            left join Information on ei.information_id = Information.i_id \
            where ei.event_id = %s and Information.timestamp<=%s and Information.timestamp>=%s',(e_id,end_time,start_time))
    result = cursor.fetchall()
    for res in result:
        print(re)
        lt = time.localtime(res['timestamp'])
        day = time.strftime('%Y-%m-%d',lt)
    query_body = {
        "query": {
        "bool": {
                "must": [
                    {"range": {"time": {"lte": td}}},
                ]
            }
        }
    }
    if index_name ==" ":
        index_name = "weibo_all"
    r = scan(es, index=index_name, query=query_body)
    '''
    user_list ={}
    user_count = 0
    pattern = re.compile(r'(\u4e2d\u56fd)')
    #pattern1 = re.compile(r'(\u9999\u6e2f|\u6fb3\u95e8|\u5b81\u590f|\u5e7f\u897f|\u65b0\u7586|\u897f\u85cf|\u5185\u8499\u53e4|\u9ed1\u9f99\u6c5f)')
    #pattern2 = re.compile(r'([\u4e00-\u9fa5]{2,5}?(\u7701|\u5e02|\u81ea\u6cbb\u533a))')  #\u7701省   \u5e02市     \u81ea\u6cbb\u533a自治区
    #result = Event.objects.filter(e_id=eid).first().information.all().filter(timestamp__range=(start_time,end_time))  #.count()
    cursor.execute('select Information.geo from Event_information ei \
            left join Information on ei.information_id = Information.i_id \
            where ei.event_id = %s and Information.timestamp<=%s and Information.timestamp>=%s',(e_id,end_time,start_time))
    result = cursor.fetchall()
    if len(result):
        for i in result:
            #print(i['geo'])
            sensitive += 1
            p = pattern.match(i['geo'])
            if p is None:
                try:
                    out_info_dict[i['geo']] += 1
                except:
                    out_info_dict[i['geo']] = 1
            else:
                try:
                    in_info_dict[i['geo']] += 1
                except:
                    in_info_dict[i['geo']] = 1

    for item in data:
        #weibo_count += 1
        #day = item['_source']["time"][0:10]
            #  后期使用if item["sentiment_polarity"]<0:
        if int(item["sentiment"])<0:
            negative += 1
        try:
            user_list[item["uid"]] = 1
        except:
            continue
        k = pattern.match(item["geo"])
        if k is None:
            try:
                out_dict[item["geo"]] += 1
            except:
                out_dict[item["geo"]] = 1
        else:
            try:
                in_dict[item["geo"]] += 1
            except:
                in_dict[item["geo"]] = 1
    user_count = len(user_list.keys())
    in_json = json.dumps(in_dict)
    out_json = json.dumps(out_dict)
    in_info_json = json.dumps(in_info_dict)
    out_info_json = json.dumps(out_info_dict)
    analyze_dict["%s_%s" %(str(end_time),e_id)] = {"event_name":e_id,
                            "hot_index":weibo_count,
                            "sensitive_index":sensitive,
                            "negative_index":negative,
                            "geo_weibo_inland":in_json,
                            "geo_weibo_outland":out_json,
                            "geo_info_inland":in_info_json,
                            "geo_info_outland":out_info_json,
                            "user_count":user_count,
                            "weibo_count":weibo_count,
                            "into_date":date,
                            "timestamp":end_time}
    sql_insert_many(cursor,"Event_Analyze", "e_id", analyze_dict)
        #print(item['_source']["geo"])
'''
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
'''
    #in_info_json = json.dumps(in_info_dict)
    #out_info_json = json.dumps(out_info_dict)
    #sql = 'insert into Event_analyze values (%s,%s,%s,%s,%s,%s)' % (e_id,e_id,all_json,sensitive_json,negative_json,thedate)
    #sql = 'insert into Event_analyze values (%s,%s,%s,%s,%s,%s)' % (e_id,e_id,pymysql.escape_string(all_json),pymysql.escape_string(sensitive_json),pymysql.escape_string(negative_json),thedate)
    #'insert into Event_Analyze(e_id,event_name,hot_index,sensitive_index,negative_index,into_date) values ("{}","{}","{}","{}","{}","{}")'.format(e_id,e_id,all_json,sensitive_json,negative_json,thedate))



if __name__ == '__main__':
    #thedate = datetime.date.today()
    '''
    sql = 'select e_id,es_index_name from Event'
    cursor.execute(sql)
    result = cursor.fetchall()
    for re in result:
        event_analyze(re['es_index_name'],re['e_id'])
    
    eid = 'xianggangshijian_1581919160'
    event_analyze("weibo_all",eid,)
    '''
    eid = 'xianggang_1582357500'
    event_analyze("xianggang_1582357500",eid,'2019-08-06')