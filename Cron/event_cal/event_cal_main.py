#-*-coding=utf-8-*-
#### 在这里导入数据函数和计算函数，写主函数进行计算
import sys
sys.path.append("../../")
from Cron.event_cal.event_analyze import event_analyze
from Cron.event_cal.event_semantic import event_semantic
from Cron.event_cal.data_utils import get_event_data


def event_cal(info, start_date, end_date):
    e_id = info['e_id']
    e_name = info['e_name']
    e_index = info['index_name']
    data = get_event_data(e_index, start_date, end_date)
    # 事件态势分析
    event_analyze(e_index,e_id)
    for date in data:
        # 事件语义分析
        event_semantic(e_id,e_name,data[date],date)



def main():
    pass

if __name__ == '__main__':
    main()