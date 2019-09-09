# -*- coding: utf-8 -*-

import time
import datetime

def today():
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))

def now():
    return time.strftime('%H:%M:%S', time.localtime(time.time()))

def date2datestr(date):
    return date.strftime('%Y-%m-%d')

def unix2hadoop_date(ts):
    return time.strftime('%Y_%m_%d', time.localtime(ts))

def ts2date(ts):
    return time.strftime('%Y-%m-%d', time.localtime(ts))

def ts2datetime(ts):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))

def date2ts(date):
    return int(time.mktime(time.strptime(date, '%Y-%m-%d')))

def datetime2ts(date):
    return int(time.mktime(time.strptime(date, '%Y-%m-%d')))

def window2time(window, size=24*60*60):
    return window*size

def datestr2ts(date):
    return time.mktime(time.strptime(date, '%Y-%m-%d'))

def nowts():
    return int(time.time())

def yesterday(theday):
    return time.strftime('%Y-%m-%d', time.localtime(datetime2ts(theday) - 24*3600))

def get_datelist(year1,month1,day1,year2,month2,day2):
    date_list = []
    begin_date = datetime.datetime.strptime(str(year1)+'-'+str(month1)+'-'+str(day1), "%Y-%m-%d")
    end_date = datetime.datetime.strptime(str(year2)+'-'+str(month2)+'-'+str(day2), "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)   #输出时间列表的函数
    return date_list

def get_datelist_v2(start_date, end_date):
    date_list = []
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    date = start_date
    while date <= end_date:
        date_str = date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        date += datetime.timedelta(days=1)   #输出时间列表的函数
    return date_list

def get_before_date(date_cha,date=None):
    # date_cha为当天日期的前几天,返回前几天的日期
    # 如当天2018-7-7,date_cha=1,则返回2018-7-6
    # 如当天2018-7-7,date_cha=-1,则返回2018-7-8
    if not date:
        today = datetime.date.today()
    else:
        today = datetime.datetime.strptime(date, '%Y-%m-%d')
    oneday = datetime.timedelta(days=date_cha)
    newday = today - oneday
    return str(newday)[:10]

