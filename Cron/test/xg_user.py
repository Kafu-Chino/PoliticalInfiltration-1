#-*-coding=utf-8-*-
import sys
import os
import time
import datetime
from elasticsearch.helpers import scan
from collections import defaultdict
from data_get_utils import sql_insert_many

sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'

from Config.db_utils import es, pi_cur, conn

cursor = pi_cur()



def get_items_from_ese_scan(index_name,date):
    #end_time = int(time.mktime(datetime.date.today().timetuple()))
    #start_time = end_time - 24 * 60 * 60
    sql = 'select f_id from Figure'
    cursor.execute(sql)
    result = cursor.fetchall()
    re = []
    for i in result:
        re.append(i['f_id'])
    #print(result)
    data_dict = defaultdict(list)
    figure_dict = defaultdict(list)
    weibo_count ={}
    query_body = {
        "query": {
        "match_all":{}
        }
    }
    r = scan(es, index=index_name, query=query_body)
    for item in r:
        uid = item['_source']["uid"]
        data_dict[uid].append(item['_source'])
    for uid in data_dict.keys():
        weibo_count[uid] = len(data_dict[uid])
    user_count = dict(sorted(weibo_count.items(),key=lambda x:x[1],reverse=True)[:10000])
    uid_list = [x for x in user_count.keys() if x not in re]
    #print(len(uid_list))
    query_body1 = {
        "query": {
            "bool": {
                "should": [
                    {"terms": {
                        "uid": uid_list
                                }
                                }
                            ]
                        }
        }
    }
    r1 = scan(es, index='weibo_user', query=query_body1)
    for item in r1:
        #drop = False
        uid = item['_source']["uid"]
        '''
        for i in result:
            if uid == i['f_id']:
                drop = True
        if drop == True:
            continue
        '''
        figure_dict[uid] = {"uid":uid,
                            "nick_name":item['_source']["nick_name"],
                            "create_at":item['_source']["create_at"],
                            "user_birth":item['_source']["user_birth"],
                            "description":item['_source']["description"],
                            "sex":item['_source']["sex"],
                            "friendsnum":item['_source']["friendsnum"],
                            "fansnum":item['_source']["fansnum"],
                            "computestatus":0,
                            "monitorstatus":1,
                            "into_date":date,
                            "user_location":item['_source']["user_location"]}
    #print(figure_dict)
    #print(len(figure_dict))
    sql_insert_many(cursor, "Figure", "f_id", figure_dict)


if __name__ == '__main__':
    thedate = datetime.date.today()
    get_items_from_ese_scan('weibo_xianggang_original',thedate)