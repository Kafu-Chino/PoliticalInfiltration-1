import numpy as np
import datetime
import math
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit
from scipy.special import gamma

import sys
sys.path.append("../../")
from Config.time_utils import *
from Config.db_utils import es,conn,pi_cur as es1,conn,pi_cur,db_connect

def func(x,a,b):
    logist = np.power(x,(a-1))*np.exp(-b*x)*np.power(b,a)/gamma(a)
    return logist
def func2(x,a):
    return a*np.exp(-a*x)

def func3(x,a,b,c):
    logist = np.power(x, (a - 1)) * np.exp(-b * x)*c
    return logist
def func4(x,a,b):
    return b * np.exp(-a * x)

def get_data(midlist,start_time,end_time):
    cursor = pi_cur()
    mids = ""
    for m in midlist:
        mids += m + ","
    sql = "select * from Informationspread where  mid in (%s) and predict = 0 and timestamp>%s and timestamp<%s order by timestamp ASC" %(','.join(['%s']*len(midlist)),start_time,end_time
                                                                                                                                              )

    # sql = "select * from Informationspread where mid in ('%s') order by timestamp ASC "% mids[:-1]
    cursor.execute(sql,midlist)
    results = cursor.fetchall()
    # print(results)
    return results


def data_process(midlist, end_time):
    message_dict = {}
    end_time = date2ts(end_time) + 86400*1
    start_time = end_time-86400*10
    for message in get_data(midlist,start_time,end_time):
        if message['mid'] in message_dict.keys():
            message['days'] = (message['store_date'] - message_dict[message['mid']]['date']).days+1
            message_dict[message['mid']]['list'].append(message)
        else:
            message['days'] = 1
            message_dict[message['mid']]={}
            message_dict[message['mid']]['list'] = []
            message_dict[message['mid']]['list'].append(message)
            message_dict[message['mid']]['date'] = message['store_date']
            message_dict[message['mid']]['message_type'] = message['message_type']
    return message_dict

def fit(m_dict):
    pre_dict = {}
    total_num = 0
    right_num = 0
    # print(m_dict)
    p0 = (0.5, 0.5)
    p1 = (0.5, 0.5)
    save_dict = {}
    for mid in m_dict.keys():
        retweet = []
        comment = []
        days = []
        if len( m_dict[mid]['list'])>3:
            save_dict[mid] = {}
            for i in m_dict[mid]['list']:
                retweet.append(i['retweet_count'])
                comment.append(i['comment_count'])
                days.append(i['days'])
            # print(m_dict[mid]['list'][len( m_dict[mid]['list'])-1])
            days_t = [m_dict[mid]['list'][len( m_dict[mid]['list'])-1]['days']+1,m_dict[mid]['list'][len( m_dict[mid]['list'])-1]['days']+2]
            re = np.array(retweet)
            co = np.array(comment)
            day = np.array(days)
            param_bounds = ([0,0], [2000000,100000])
            try:
                popt1, pcov1 = curve_fit(func4, day, co,maxfev=10000,p0=p0,bounds=param_bounds)#,p0=p0,bounds=param_bounds)
            except:
                popt1 = p0
            p0 = popt1
            # print(p0)
            try:
                popt2, pcov2 = curve_fit(func4, day, re,maxfev=10000,p0=p1,bounds=param_bounds)#,p0=p1,bounds=param_bounds)
            except:
                popt2 = p1
            p1 = popt2
            # print(p1)
            #验证
            retweet_pred = [func4(i, popt2[0], popt2[1]) for i in days_t]#, popt1[1]

            for i in range(len(retweet_pred)):
                if retweet_pred[i]<1:
                    retweet_pred[i] = 0
                elif retweet_pred[i]>100:
                    retweet_pred[i] = retweet_pred[i]*0.05
                elif retweet_pred[i]>10:
                    retweet_pred[i] = retweet_pred[i]*0.1
            # print(retweet_pred)
            # for i in range(len(retweet_pred)):
            #     total_num += 1
            #     if retweet_t[i] != 0:
            #         if retweet_pred[i] >0:
            #             if int(math.log(retweet_t[i])) == int(math.log(retweet_pred[i])):
            #                 right_num += 1
            #         else:
            #             if retweet_t[i]<10:
            #                 right_num +=1
            #     else:
            #         if int(retweet_pred[i])<10:
            #             right_num += 1
            comment_pred = [func4(i, popt1[0], popt1[1]) for i in days_t]#, popt2[1]
            for i in range(len(comment_pred)):
                if comment_pred[i]<1:
                    comment_pred[i] = 0
                elif comment_pred[i] > 100:
                    comment_pred[i] = comment_pred[i] * 0.05
                elif comment_pred[i]>10:
                    comment_pred[i] = comment_pred[i]*0.1
            # print(comment_pred)
            for i in range(len(days_t)):
                date = str(m_dict[mid]['date'] + datetime.timedelta(days_t[i]-1))[:10]
                save_dict[mid][date] = {}
                save_dict[mid][date]['retweet'] = retweet_pred[i]
                save_dict[mid][date]['comment'] = comment_pred[i]
                save_dict[mid][date]['message_type'] = m_dict[mid]['message_type']
    # print(save_dict)
    save(save_dict)


def save(save_dict):
    val = []
    for mid in save_dict:
        # print(mid)
        for date in save_dict[mid]:
            timestamp = date2ts(date)
            val.append((str(timestamp) + "_" + mid,mid,timestamp,int(save_dict[mid][date]['retweet']),int(save_dict[mid][date]['comment']),save_dict[mid][date]['message_type'],date,1))
    sql = 'replace into Informationspread(is_id,mid,timestamp,retweet_count,comment_count,message_type,store_date,predict) values (%s,%s,%s,%s,%s,%s,%s,%s )'
    cursor = conn.cursor()
    try:
        cursor.executemany(sql, val)
        conn.commit()
    except:
        conn.rollback()
        print('错误')

def prediction(mid_dic, date):
    midlist = []
    for item in mid_dic:
        midlist.append(item['mid'])
    print("开始进行传播预测")
    fit(data_process(midlist, date))
    print("传播预测结束")








if __name__ == '__main__':
    fit(data_process(["c_4406640931952257","c_4406683806166512"]))