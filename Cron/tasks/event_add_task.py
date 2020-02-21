import sys
sys.path.append('../../')


from Config.time_utils import *
from Config.db_utils import es, pi_cur, conn, get_event_para
from Cron.event_cal.data_utils import get_edic_add, save_event_data, sensitivity_store, \
    event_sensitivity
from Cron.event_cal.event_cal_main import event_cal
from Cron.event_cal.sensitive_word_filter import sensitive_word_filter
from Cron.event_cal.sensitivity import sensitivity
from Cron.event_cal.figure_add import figure_add


# 更新事件库计算状态
def update_cal_status(eid, cal_status):
    cursor = pi_cur()
    sql = "UPDATE Event SET cal_status = %s WHERE e_id = %s"

    params = [(cal_status, eid)]
    n = cursor.executemany(sql, params)
    conn.commit()


# 更新事件库监测状态
def update_monitor_status(eid, status):
    cursor = pi_cur()
    sql = "UPDATE Event SET monitor_status = %s WHERE e_id = %s"

    params = [(status, eid)]
    n = cursor.executemany(sql, params)
    conn.commit()


# 对新添加的事件进行计算，在bash里定义5分钟一运行
def event_add(date):
    # 获取新添加的事件
    eid_dic = get_edic_add()

    # 分事件进行计算
    print("需要计算事件 {} 个。".format(len(eid_dic)))
    for e_item in eid_dic:
        e_id = e_item['e_id']
        e_name = e_item['event_name']
        e_index = e_item['es_index_name']
        start_date = e_item['begin_date']
        end_date = e_item['end_date']
        try:
            SENTIMENT_NEG = get_event_para(e_id, 'sentiment_neg')
        except:
            SENTIMENT_NEG = 0.2
        try:
            SENTIMENT_POS = get_event_para(e_id, 'sentiment_pos')
        except:
            SENTIMENT_POS = 0.7
        try:
            POS_NUM = get_event_para(e_id, 'pos_num')
        except:
            POS_NUM = 1000
        try:
            NEG_NUM = get_event_para(e_id, 'neg_num')
        except:
            NEG_NUM = 15000
        # 更新为“计算中”
        update_cal_status(e_id, 1)

        # 获取事件相关微博，计算情感极性，并存入事件索引（没有索引就创建一个）
        save_event_data(e_id, 0, SENTIMENT_POS, SENTIMENT_NEG)

        # 对新获取的事件相关微博进行敏感词过滤
        data_dict = sensitive_word_filter(0, e_id)

        # 对过滤后的结果进行敏感计算
        data_dict = sensitivity(e_id, data_dict, e_index, POS_NUM, NEG_NUM)

        # 敏感信息入库,敏感信息和事件关联入库
        sensitivity_store(data_dict)
        event_sensitivity(e_id,data_dict)

        # 敏感人物入库,敏感人物和事件关联入库
        figure_add(data_dict,e_id)

        # 事件计算
        event_cal(e_item,start_date,end_date)

        # 更新为“计算完成”
        update_cal_status(e_id, 2)

        # 更新为“监测中”
        update_monitor_status(e_id, 1)

        print("事件 %s 已添加成功，并计算完成。" % e_name)


if __name__ == '__main__':
    date = today()
    # date = '2019-08-26'
    event_add(date)