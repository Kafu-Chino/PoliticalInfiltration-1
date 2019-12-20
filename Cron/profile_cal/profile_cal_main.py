#### 在这里导入数据函数和计算函数，写主函数进行计算
#### 可以根据需求，在profile_cal_uidlist和main函数里加入多进程计算或分布式计算，现在单进程顺序操作即可

from data_get_utils import get_items_from_uidList, get_data_dict, sql_insert_many
import math
#from .data_get_utils import *
from user_position import *
from user_msg_type import *
from user_topic import get_user_topic
from user_domain import get_user_domain
from user_social import get_user_social
from user_keywords import get_user_keywords
from data_process_utils import get_processed_data


def profile_cal_uidlist(uidlist):
	data = get_items_from_uidList(uidlist)
    result_position = get_user_activity_aggs(data)
    result_msg_type = get_msg_type_aggs(data)
    sql_insert_many(cursor, "UserBehavior", "ub_id", result_msg_type)
    sql_insert_many(cursor, "UserActivity", "ua_id", result_position)
	print(data)
	word_dict,text_list = get_processed_data(data)
	get_user_topic(word_dict)
	get_user_domain(word_dict)
	get_user_social(data)
	get_user_keywords(text_list,word_dict,5)


def main():
    uidlist = get_uid_list(cursor, "Figure", "uid")
    uidlist_new = []
    n = math.ceil(len(uidlist) / 1000)
    for i in range(n):
        uids = uidlist[i * 1000, (i + 1) * 1000]
        uidlist_new.append(uids)
    for uidlist_sub in uidlist_new:
        profile_cal_uidlist(uidlist_sub)


if __name__ == '__main__':
	uid_list=["5241560394","6598780267"]
	data =  {'5241560394': [{'source': '新浪', 'uid': '5241560394', 'root_uid': '', 'mid': '4404755222396058', 'root_mid': '', 'time': '2019-08-13 09:15:44', 'message_type': 1, 'sentiment': '0', 'text': '#外国人香港机场教训示威者# 看了这个视频我终于知道了什么叫:你永远滋不醒一个张嘴接尿的人http://t.cn/AiHh83xh ', 'geo': '\x08(国外未知未知)', 'net_type': '荣耀20 PRO', 'user_fansnum': 43, 'timestamp': 1565658944.0}], '6598780267': [{'source': '新浪', 'uid': '6598780267', 'root_uid': '', 'mid': '4404757026037564', 'root_mid': '', 'time': '2019-08-13 09:22:54', 'message_type': 1, 'sentiment': '-15', 'text': '#搜狐资讯#《香港机场再遭示威者瘫痪 今日余下航班全部取消》大批示威者今天聚集香港国际机场（联合早报网）海外网8月12日http://t.cn/AiHZDiWp ', 'geo': '中国移动(国外未知未知)', 'net_type': '搜狐资讯', 'user_fansnum': 3, 'timestamp': 1565659374.0}, {'source': '新浪', 'uid': '6598780267', 'root_uid': '', 'mid': '4405455973350546', 'root_mid': '', 'time': '2019-08-15 07:40:16', 'message_type': 1, 'sentiment': '-9', 'text': '#搜狐资讯#《内地记者在香港机场被示威者拘押殴打 被警方 救出》13日晚，环球网记者付国豪在香港机场被示威者非法拘押，遭到非http://t.cn/AiHiTdKD ', 'geo': '中国移动(国外未知未知)', 'net_type': '搜狐资讯', 'user_fansnum': 3, 'timestamp': 1565826016.0}]}
	word_dict,text_list = get_processed_data(data)
	#print(word_dict)
	#get_user_topic(word_dict)
	#get_user_domain(word_dict)
	get_user_social(data)
	get_user_keywords(text_list,word_dict,5)