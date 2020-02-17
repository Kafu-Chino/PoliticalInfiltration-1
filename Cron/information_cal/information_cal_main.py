import os
import sys
import math

sys.path.append("../../")

from Cron.information_cal.data_utils import get_mid_dic
from Cron.information_cal.information_hazard import get_trend

def main(start_date, end_date):
    mid_dic = get_mid_dic()
    batch_num = 10000
    batch_all = math.ceil(len(mid_dic) / batch_num)
    for batch_epoch in range(batch_all):
        mid_dic_batch = mid_dic[batch_epoch * batch_num: (batch_epoch + 1) * batch_num]
        print("信息{}至{}， 共{}".format(batch_epoch * batch_num, (batch_epoch + 1) * batch_num, len(mid_dic)))

        get_trend(mid_dic_batch, start_date, end_date)

if __name__ == '__main__':
    start_date = "2019-08-22"
    end_date = "2019-08-22"
    main(start_date, end_date)