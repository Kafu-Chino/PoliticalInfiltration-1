#-*-coding=utf-8-*-
#### 在这里导入数据函数和计算函数，写主函数进行计算
import sys
sys.path.append("../../")
from Config.db_utils import get_event_para
from Cron.event_cal.event_analyze import event_analyze
from Cron.event_cal.event_semantic import event_semantic
from Cron.event_cal.event_hashtag_senwords import event_hashtag_senwords
from Cron.event_cal.data_utils import get_event_data, save_event_data, sensitivity_store, \
    event_sensitivity
from Cron.event_cal.sensitive_word_filter import sensitive_word_filter
from Cron.event_cal.sensitivity import sensitivity
from Cron.event_cal.figure_add import figure_add


def event_cal_main(info, n, start_date, end_date):
    """
    事件主计算函数
    :param info: 事件信息，包括id，name，index_name，开始结束时间等
    :param n: 是否为新添加事件。1为日常计算，0为新添加
    :param start_date: 计算开始时间
    :param end_date: 计算结束时间
    :return: 无
    """
    e_id = info['e_id']
    e_name = info['event_name']
    e_index = info['es_index_name']

    # 获取事件相关计算参数
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
    try:
        WEIBO_NUM = get_event_para(e_id, 'weibo_num')
    except:
        WEIBO_NUM = 100000

    print('获取事件相关微博')
    # 获取事件相关微博，计算情感极性，并存入事件索引（没有索引就创建一个）
    save_event_data(e_id, n, SENTIMENT_POS, SENTIMENT_NEG)

    print('敏感词过滤')
    # 对新获取的事件相关微博进行敏感词过滤
    data_dict = sensitive_word_filter(n, e_id)

    print('敏感词过滤')
    # 对过滤后的结果进行敏感计算
    data_dict = sensitivity(e_id, data_dict, e_index, POS_NUM, NEG_NUM)

    print('敏感信息入库')
    # 敏感信息入库,敏感信息和事件关联入库
    sensitivity_store(data_dict)
    event_sensitivity(e_id, data_dict)

    print('敏感人物入库')
    # 敏感人物入库,敏感人物和事件关联入库
    figure_add(data_dict, e_id)

    print('事件计算')
    # 获取微博文本数据进行分析
    data_dict = get_event_data(e_index, start_date, end_date)

    # 事件态势分析
    event_analyze(e_index, e_id)

    for date in data_dict:
        # 事件语义分析
        event_semantic(e_id, e_name, data_dict[date], date, WEIBO_NUM)

        # 事件特殊分析（hashtag、敏感词分布）
        event_hashtag_senwords(e_id, data, date)


def main():
    data_dict = get_event_data("weibo_all", "2019-08-20", "2019-08-20")
    print(len(data_dict["2019-08-20"]))
    event_hashtag_senwords("xianggangshijian_1581919160", data_dict["2019-08-20"], "2019-08-20")

if __name__ == '__main__':
    main()
