import re
import sys
import json
sys.path.append("../../")

from Config.db_utils import es, pi_cur, conn

def cal_hashtag(e_id, data, date):
	hashtag_dic = {}
	global_senwords_dic = {}
	event_senwords_dic = {}

	global_senwords_list = []
	event_senwords_list = []
	re_global_senwords = re.compile('|'.join(global_senwords_list))
	re_event_senwords = re.compile('|'.join(event_senwords_list))

    re_hashtag = re.compile('#.+?#')

	for text in data:
		for hashtag in re_hashtag.findall(text):
			if hashtag in hashtag_dic:
				hashtag_dic[hashtag] += 1
			else:
				hashtag_dic[hashtag] = 1

		for global_senword in re_global_senwords.findall(text):
			if global_senword in global_senwords_dic:
				global_senwords_dic[global_senword] += 1
			else:
				global_senwords_dic[global_senword] = 1

		for event_senword in re_event_senwords.findall(text):
			if event_senword in event_senwords_dic:
				event_senwords_dic[global_senword] += 1
			else:
				event_senwords_dic[global_senword] = 1

	result = json.dumps(result)
    timestamp = date2ts(thedate)
    es_id = timestamp + e_id
    sql = "REPLACE into Event_Semantic values(%s,%s,%s,%s,%s,%s)"
    val = [(es_id,e_id,e_name,result,timestamp,thedate)]
    try:
        n = cursor.executemany(sql, val)
        print("insert %d success" % n)
        conn.commit()
    except:
        print('出现数据库错误')