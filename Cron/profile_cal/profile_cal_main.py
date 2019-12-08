#### 在这里导入数据函数和计算函数，写主函数进行计算
#### 可以根据需求，在profile_cal_uidlist和main函数里加入多进程计算或分布式计算，现在单进程顺序操作即可

from data_get_utils import get_items_from_uidList, get_data_dict, sql_insert_many
from user_position import xxx
from user_msg_type import yyy

def profile_cal_uidlist(uidlist):
	data = get_items_from_uidList(uidlist)
	result_position = xxx(data)
	result_msg_type = yyy(data)
	sql_insert_many(result_position)
	sql_insert_many(result_msg_type)

def main():
	uidlist = get_data_dict()
	for uidlist_sub in uidlist:
		profile_cal_uidlist(uidlist_sub)

if __name__ == '__main__':
	main()