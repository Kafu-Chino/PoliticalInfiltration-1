import os
import sys
import math

sys.path.append("../../")

from Cron.information_cal.information_hazard import get_trend
from Cron.information_cal.data_utils import get_mid_dic_all
from Cron.information_cal.Spread_prediction import prediction


def information_cal_batch(mid_dic_batch, start_date, end_date):

    # 计算信息传播态势和危害指数
    get_trend(mid_dic_batch, start_date, end_date)
    prediction(mid_dic_batch, end_date)


if __name__ == '__main__':
    pass