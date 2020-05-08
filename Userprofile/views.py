# -*- coding: utf-8 -*-
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum,Avg
import time
import datetime
from collections import defaultdict
from django.db.models import Q,Count
from Userprofile.models import *
from Mainevent.models import *
from Config.base import *
from Config.time_utils import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema
import json
import operator


class Test(APIView):
    """测试页面"""

    def get(self, request):
        """GET方法的功能说明写在这里"""
        return HttpResponse('这是测试的GET方法')

    def post(self, request):
        """POST方法的功能说明写在这里"""
        return HttpResponse('这是测试的POST方法')

    def put(self, request):
        """PUT方法的功能说明写在这里"""
        return HttpResponse('这是测试的PUT方法')

    def delete(self, request):
        """DELETE方法的功能说明写在这里"""
        return HttpResponse('这是测试的DELETE方法')




class User_Behavior(APIView):
    """用户活动特征接口"""

    def get(self, request):
        """
        获取uid，返回用户活动特征详情，根据传入参数n_type 日 周 月 返回相应数据结果，
        返回数据格式{date1:{originalnum_s:10,commentnum_s:20,retweetnum_s:30,sensitivenum_s:10},
                    date2:{originalnum_s: 10,commentnum_s:20,retweetnum_s:30,sensitivenum_s:10},
                    ...}
        """
        uid = request.GET.get('uid')
        n_type = request.GET.get('n_type')
        #date = request.GET.get('date')
        res_dict = defaultdict(dict)
        #origin_dict = {}
        #comment_dict={}
        try:
            date = UserBehavior.objects.filter(uid=uid).order_by('-store_date')[0].store_date.strftime('%Y-%m-%d')
        except:
            date = today()
        #t= date2ts(date)
        t=datetime.datetime(*map(int, date.split('-')))
        #print(date)
        date_dict = {}
        #t=datetime.datetime.strptime(date+ " 23:59:59", '%Y-%m-%d %H:%M:%S')
        #t = time.mktime(time.strptime(date, '%Y-%m-%d'))
        # 每日活动特征，从当前日期往前推7天展示 原创微博数、评论数、转发数、敏感微博数
        if n_type == "日":
            #time1 = time.time()
            date = date2ts(date)
            dl = get_datelist_v2(ts2date(date - 149 * 86400),ts2date(date))
            #new_date = (t + datetime.timedelta(days=-150)).timestamp()
            #date_dict[0] = new_date
            #for i in range(150):
                #date_dict[i + 1] = (t + datetime.timedelta(-150+1 * (i + 1))).timestamp()
                #item = UserBehavior.objects.filter(uid=uid, timestamp__gte=date_dict[i],timestamp__lt=date_dict[i+1]).values(
                    #"store_date",'originalnum','commentnum','retweetnum','sensitivenum')   #.order_by("timestamp")
                #d = time.strftime("%Y-%m-%d", time.localtime((date_dict[i])))
                #print(item)
            for d in dl:
                item = UserBehavior.objects.filter(uid=uid, store_date__gte=d,store_date__lte=d).values(
                    "store_date",'originalnum','commentnum','retweetnum','sensitivenum')
                if item.exists():
                    #res_dict['date'].append(item["store_date"])
                    #res_dict[time.strftime("%Y-%m-%d", time.localtime(t))] = item
                    #res_dict[str(td)] = item
                    res_dict['originalnum'][d] = item[0]['originalnum']
                    res_dict['commentnum'][d] = item[0]['commentnum']
                    res_dict['retweetnum'][d] = item[0]['retweetnum']
                    res_dict['sensitivenum'][d] = item[0]['sensitivenum']
                    '''
                    if item['originalnum_s']:
                        res_dict['originalnum'].append(item['originalnum_s']) 
                    else:
                        res_dict['originalnum'].append(0) 
                    if item['commentnum_s']:
                        res_dict['commentnum'].append(item['commentnum_s'])
                    else:
                        res_dict['commentnum'].append(0)
                    if item['retweetnum_s']:
                        res_dict['retweetnum'].append(item['retweetnum_s'])
                    else:
                        res_dict['retweetnum'].append(0)
                    if item['sensitivenum_s']:
                        res_dict['sensitivenum'].append(item['sensitivenum_s'])
                    else:
                        res_dict['sensitivenum'].append(0)
                    '''
                else:
                    #td = ts2date(date_dict[i])
                    #res_dict['date'].append(ts2date(date_dict[i+1]))
                    res_dict['originalnum'][d] = 0
                    res_dict['commentnum'][d] = 0
                    res_dict['retweetnum'][d] = 0
                    res_dict['sensitivenum'][d] = 0
        # 每周活动特征，从当前日期往前推5周展示 原创微博数、评论数、转发数、敏感微博数
        if n_type == "周":
            date_dict[0] = (t + datetime.timedelta(weeks=-22)).timestamp()
            for i in range(22):
                date_dict[i + 1] = (t + datetime.timedelta(weeks=(-22 + 1 * (i + 1)))).timestamp()
            #date_dict[0] = t.timestamp()
            #for i in range(22):
                result = UserBehavior.objects.filter(uid=uid, timestamp__gte=date_dict[i],
                                                     timestamp__lt=date_dict[i+1]).aggregate(
                    originalnum_s=Sum("originalnum"), commentnum_s=Sum("commentnum"), retweetnum_s=Sum("retweetnum"),
                    sensitivenum_s=Sum("sensitivenum"))
                #if list(result.values())[0]:
                print(result)
                td = time.strftime("%Y-%m-%d", time.localtime((date_dict[i])))
                if len(result):  #.exists():
                    #res_dict['date'].append(time.strftime("%Y-%m-%d", time.localtime((date_dict[i]))))
                    if result['originalnum_s']:
                        res_dict['originalnum'][td] = result['originalnum_s']
                    else:
                        res_dict['originalnum'][td] = 0
                    if result['commentnum_s']:
                        res_dict['commentnum'][td] = result['commentnum_s']
                    else:
                        res_dict['commentnum'][td] = 0
                    if result['retweetnum_s']:
                        res_dict['retweetnum'][td] = result['retweetnum_s']
                    else:
                        res_dict['retweetnum'][td] = 0
                    if result['sensitivenum_s']:
                        res_dict['sensitivenum'][td] = result['sensitivenum_s']
                    else:
                        res_dict['sensitivenum'][td] = 0
                else:
                    res_dict['originalnum'][td] = 0
                    res_dict['commentnum'][td] = 0
                    res_dict['retweetnum'][td] = 0
                    res_dict['sensitivenum'][td] = 0
        # 每月活动特征，从当前日期往前推5月展示 原创微博数、评论数、转发数、敏感微博数
        if n_type == "月":
            date_dict[0] = (t + datetime.timedelta(days=-150)).timestamp()
            for i in range(5):
                date_dict[i + 1] = (t + datetime.timedelta(days=(-150 + 30 * (i + 1)))).timestamp()
            #date_dict[0] = t.timestamp()
            #for i in range(5):
                result = UserBehavior.objects.filter(uid=uid, timestamp__gte=date_dict[i],
                                                     timestamp__lt=date_dict[i+1]).aggregate(
                    originalnum_s=Sum("originalnum"), commentnum_s=Sum("commentnum"), retweetnum_s=Sum("retweetnum"),
                    sensitivenum_s=Sum("sensitivenum"))
                td = time.strftime("%Y-%m", time.localtime((date_dict[i])))
                print(result)
                if len(result):
                    if result['originalnum_s']:
                        res_dict['originalnum'][td] = result['originalnum_s']
                    else:
                        res_dict['originalnum'][td] = 0
                    if result['commentnum_s']:
                        res_dict['commentnum'][td] = result['commentnum_s']
                    else:
                        res_dict['commentnum'][td] = 0
                    if result['retweetnum_s']:
                        res_dict['retweetnum'][td] = result['retweetnum_s']
                    else:
                        res_dict['retweetnum'][td] = 0
                    if result['sensitivenum_s']:
                        res_dict['sensitivenum'][td] = result['sensitivenum_s']
                    else:
                        res_dict['sensitivenum'][td] = 0
        n_res = defaultdict(dict)
        n_res['date'] = list(res_dict['originalnum'].keys())
        n_res['originalnum'] = list(res_dict['originalnum'].values())
        n_res['commentnum'] = list(res_dict['commentnum'].values())
        n_res['retweetnum'] = list(res_dict['retweetnum'].values())
        n_res['sensitivenum'] = list(res_dict['sensitivenum'].values())
        #time2 = time.time()
        #print(time2-time1)
        return JsonResponse(n_res,safe=False,json_dumps_params={'ensure_ascii':False})



'''
class User_Behavior(APIView):
    """用户活动特征接口"""

    def get(self, request):
        """
        获取uid，返回用户活动特征详情，根据传入参数n_type 日 周 月 返回相应数据结果，
        返回数据格式{date1:{originalnum_s:10,commentnum_s:20,retweetnum_s:30,sensitivenum_s:10},
                    date2:{originalnum_s: 10,commentnum_s:20,retweetnum_s:30,sensitivenum_s:10},
                    ...}
        """
        uid = request.GET.get('uid')
        #n_type = request.GET.get('n_type')
        #date = request.GET.get('date')
        res_dict = defaultdict(dict)
        #origin_dict = {}
        #comment_dict={}

        #t=datetime.datetime.strptime(date+ " 23:59:59", '%Y-%m-%d %H:%M:%S')
        #t = time.mktime(time.strptime(date, '%Y-%m-%d'))
        #new_date = (t + datetime.timedelta(days=-7)).timestamp()
        result = UserBehavior.objects.filter(uid=uid).values(
                "store_date").annotate(originalnum_s=Sum("originalnum"), commentnum_s=Sum("commentnum"),
                                      retweetnum_s=Sum("retweetnum"), sensitivenum_s=Sum("sensitivenum"))
        if result.exists():
            for item in result:
                td = item["store_date"]  #pop("timestamp") - 24 * 60 * 60
                res_dict['originalnum'][str(td)] = item['originalnum_s']
                res_dict['commentnum'][str(td)] = item['commentnum_s']
                res_dict['retweetnum'][str(td)] = item['retweetnum_s']
                res_dict['sensitivenum'][str(td)] = item['sensitivenum_s']
            return JsonResponse(res_dict,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "未找到该用户活动信息"},safe=False,json_dumps_params={'ensure_ascii':False}) 
'''
import re
class User_Activity(APIView):
    """用户地域特征接口"""

    def get(self, request):
        """
        获取uid，返回用户地域特征详情，根据地理位置、IP段，展示当日、前7天、前30天、前90天敏感微博数降序排序;
        n_type对应关系,默认n_type=3:
                        {"1":day_date,"2":week_date,"3":month_date,"4":threemonth_date}
        返回数据格式{
                    "day_result":[{"geo1":geo_name,"send_ip":ips,"statusnum_s":30,"sensitivenum_s":10},{},...],
                    "geo_map_result":[{"geo1":geo_name,"statusnum_s":30},{},..],
                    "route_list":[{"s":geo,"e":geo},{s":geo,"e":geo},...]
                }
        """
        uid = request.GET.get('uid')
        n_type = int(request.GET.get('n_type')) if request.GET.get('n_type') else 3
        #date = request.GET.get('date')
        #t=datetime.datetime.strptime(date+ " 23:59:59", '%Y-%m-%d %H:%M:%S')
        try:
            date = UserActivity.objects.filter(uid=uid).order_by('-store_date')[0].store_date.strftime('%Y-%m-%d')
        except:
            date = today()
        #print(date)
        t=datetime.datetime(*map(int, date.split('-')))
        #t= time.mktime(time.strptime(date, '%Y-%m-%d'))
        print(t,n_type)
        date_dict = {}
        res_dict = defaultdict(list)
        geo_result = defaultdict(dict)
        if n_type == 1:
            cal_date = t + datetime.timedelta(days=-1)
        if n_type == 2:
            cal_date = t + datetime.timedelta(days=-7)
        if n_type ==3:
            cal_date = t + datetime.timedelta(days=-30)
        if n_type ==4:
            cal_date = t + datetime.timedelta(days=-90)
        #cal_date = (t + datetime.timedelta(days=-30))  #.timestamp()
        cal_date = cal_date.strftime('%Y-%m-%d')
        print(cal_date)
        day_result = UserActivity.objects.filter(uid=uid, store_date__gte=cal_date,store_date__lte=t).values("geo", "send_ip")  \
               .annotate(statusnum_s=Sum("statusnum"), sensitivenum_s=Sum("sensitivenum")).order_by("-statusnum_s")[:5]   #之前按敏感微博总数
        #print(day_result)
        pattern = re.compile(r'(\u4e2d\u56fd)')
        pattern2 = re.compile(r'(\u672a\u77e5)')
        '''
        for res in day_result:
            try:
                geo_result[res['geo']]['statusnum_s'] += res['statusnum']
                geo_result[res['geo']]['sensitivenum_s'] += res['sensitivenum']
                geo_result[res['geo']]['send_ip'] = res['send_ip']
            except:
                geo_result[res['geo']]['statusnum_s'] = res['statusnum']
                geo_result[res['geo']]['sensitivenum_s'] = res['sensitivenum']
                geo_result[res['geo']]['send_ip'] = res['send_ip']
        print(geo_result)
        if day_result.exists():
            for res in day_result:
                p = pattern.match(res['geo'])
                if p is None:
                    p2 = pattern2.match(res['geo'])
                    if p2 is None:
                        geo = res['geo'].split('&')[0]
                else:
                    geo = res['geo'].split('&')[1]
                res_dict["day_result"].append({'geo':geo,"statusnum_s":res['statusnum_s'],"sensitivenum_s":res['sensitivenum_s'],'send_ip':res['send_ip']})
        else:
            res_dict["day_result"] = {"geo":None,"send_ip":None,"statusnum_s":None,"sensitivenum_s":None}
            '''
        if day_result.exists():
            res_dict["day_result"]=list(day_result)
        else:
            res_dict["day_result"] = {"geo":None,"send_ip":None,"statusnum_s":None,"sensitivenum_s":None}
        geo_map_result = UserActivity.objects.filter(uid=uid, store_date__gte=cal_date).values("geo").annotate(
            statusnum_s=Sum("statusnum")).order_by("-statusnum_s")
        #print(geo_map_result)
        #res_dict["geo_map_result"] = list(geo_map_result)
        if geo_map_result.exists():
            for item in geo_map_result:
                p = pattern.match(item['geo'])
                if p is None:
                    continue
                else:
                    try:
                        p2 = pattern2.match(item['geo'].split('&')[1])
                        if p2 is None:
                            geo = item['geo'].split('&')[1]
                            value = item["statusnum_s"]
                        else:
                            geo = None
                            value = None
                    except:
                        geo = None
                        value = None
                res_dict["geo_map_result"].append({"name":geo,"value":value})
        else:
            res_dict["geo_map_result"].append({"name":None,"value":None})

        return JsonResponse(res_dict,safe=False,json_dumps_params={'ensure_ascii':False})



def insertData(e_name, *figure_names):
    cour_name = []

    for f in figure_names:
        try:
            figure = Figure.objects.get(uid=f)
        except Figure.DoesNotExist:
            figure = Figure.objects.create(uid=f)
        cour_name.append(figure)
    e = Event(e_id=str(int(time.time())), event_name=e_name, begin_timestamp=10110000, begin_date=datetime.date.today())
    e.save()
    e.figure.add(*cour_name)


class Show_topic(APIView):
    """展示用户的话题和领域
       输入uid
       输出{“topics”：{“uid”:{“topic1”:p,…}}}"""
    def get(self,request):
        #re = defaultdict(list)
        re2 = []
        #prefer = defaultdict(dict)
        uid = request.GET.get("uid")
        #start_date = request.GET.get("date")
        #start_date = datetime.datetime.strptime(start_date,"%Y-%m-%d")
        #end_date = start_date + datetime.timedelta(days=7)
        result1 = UserTopic.objects.filter(uid = uid) #,store_date__range=(start_date,end_date))
        #result2 = UserDomain.objects.filter(uid = uid)  #, store_date__range=(start_time,end_time)
        if result1.exists():
            json_data = serializers.serialize("json",result1)
            results = json.loads(json_data)
            new_topic={}
            for i in results:
                #uid = i["fields"]["uid"]
                for item in i["fields"]["topics"]:
                    #print(topic_dict['anti_corruption'])
                    #print(i["fields"]["topics"][item])
                    try:
                        new_topic[topic_dict[item]] += i["fields"]["topics"][item]
                    except:
                        new_topic[topic_dict[item]] = i["fields"]["topics"][item]
                    #print(new_topic)
            re = sorted(new_topic.items(),key=lambda x:x[1],reverse=True)[:5]
            count = 0
            for item in re:
                count += item[1] 
            for item in re:
                value = item[1]/count
                re2.append({"name":item[0],"value":'%.2f' % value})
            #print(type(re))
            #re = json.dumps(re,ensure_ascii=False)
            #re = json.load(re,ensure_ascii=False)
            return JsonResponse(re2,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "未找到该用户信息"},safe=False,json_dumps_params={'ensure_ascii':False}) 




class Show_keyword(APIView):
    """展示用户关键词、参与话题、敏感词
       输入uid
       输出{‘uid’:{‘keywords’:{…},’sensitive_words’:{},’hastags’:{}}"""
    def get(self,request):
        re1 = defaultdict(list)
        uid = request.GET.get("uid")
        #end_date = request.GET.get("date")
        #end_date = datetime.datetime.strptime(end_date,"%Y-%m-%d")
        #start_date = end_date - datetime.timedelta(days=7)
        kw= {}
        sw = {}
        ht = {}
        #start_time = request.GET.get("time1")
        #end_time = request.GET.get("time2")
        result = UserKeyWord.objects.filter(uid = uid)  #, store_date__range=(start_date,end_date))
        #return HttpResponse(typeof(result))
        if result.exists():
            json_data = serializers.serialize("json",result)
            results = json.loads(json_data)
            #return JsonResponse(results,safe=False)
            for i in results:
                #uid = i["fields"]["uid"]
                #re1[uid].append({"keywords":i["fields"]["keywords"],"sensitive_words":i["fields"]["sensitive_words"],"hastags":i["fields"]["hastags"]})
                for k,v in i["fields"]["keywords"].items():
                    try:
                        kw[k] += v
                    except:
                        kw[k] = v
                for k,v in i["fields"]["sensitive_words"].items():
                    try:
                        sw[k] += v
                    except:
                        sw[k] = v 
                for k,v in i["fields"]["hastags"].items():
                    try:
                        ht[k] += v
                    except:
                        ht[k] = v
                #re1["keywords"] = dict(sorted(kw.items(),key=lambda x:x[1],reverse=True)[:5])
                #re1["sensitive_words"] = sw
                #re1["hastags"] = dict(sorted(ht.items(),key=lambda x:x[1],reverse=True)[:5])
            key = sorted(kw.items(),key=lambda x:x[1],reverse=True)[:5]
                #print(sw)
            for item in key:
                re1["keywords"].append({"name":item[0],"value":'%.4f' % item[1]})
            if len(ht):
                has = sorted(ht.items(),key=lambda x:x[1],reverse=True)[:5]
                for item in has:
                    re1["hastags"].append({"name":item[0],"value":item[1]})
            else:
                re1["hastags"]=[]
            if len(sw):
                for k,v in sw.items():
                    #print(item)
                    re1["sensitive_words"].append({"name":k,"value":v})
            else:
                re1["sensitive_words"]=[]
            return JsonResponse(re1,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "未找到该用户信息"},safe=False,json_dumps_params={'ensure_ascii':False})

# 社交特征完整功能接口
class Show_contact_wanquanban(APIView):
    def get(self,request):
        uid = request.GET.get("uid")
        date_window = int(request.GET.get("date_window", 30))
        min_count = int(request.GET.get("min_count", 1))
        max_count = int(request.GET.get("max_count", 9999999999))

        # 时间范围内的数据获取，该用户上游和下游的节点连接
        try:
            end_date = Event.objects.filter(figure__uid=uid).order_by('end_date')[0].end_date.strftime('%Y-%m-%d')
        except:
            end_date = today()
        end_ts = date2ts(end_date)
        start_ts = end_ts - date_window * 86400

        result = UserSocialContact.objects.filter((Q(source=uid) | Q(target=uid)) & Q(timestamp__gte=start_ts) & Q(timestamp__lte=end_ts)).values()
        # return JsonResponse({1:list(result)}, safe=False)

        # 对用户多日的数据进行聚合
        result_sta = {}
        for item in result:
            key = (item['source'], item['target'])
            source_name = item['source_name'] if item['source_name'] else item['source']
            target_name = item['target_name'] if item['target_name'] else item['target']
            if key not in result_sta:
                result_sta[key] = {
                    "message_type":{
                        2: 0,
                        3: 0
                    },
                    "name": (source_name, target_name)
                }
            result_sta[key]["message_type"][item['message_type']] += item["count"]

        # 形成节点、边的列表，展示节点和边的属性
        node_list = []
        link_list = []
        max_num = 0
        min_num = 9999999999
        node_set = set([])
        for key in result_sta:
            # 去掉自环节点
            if key[0] == key[1]:
                continue

            for message_type in result_sta[key]["message_type"]:
                count = result_sta[key]["message_type"][message_type]
                if count:
                    max_num = max(count, max_num)
                    min_num = min(count, min_num)
                if count >= min_count and count <= max_count:
                    node_link = {
                        'source': key[0],
                        'target': key[1],
                        'message_type': message_type,
                        'count': result_sta[key]["message_type"][message_type]
                    }
                    link_list.append(node_link)

                    if key[0] not in node_set:
                        source_node = {'id': key[0], 'name': result_sta[key]["name"][0]}
                        node_list.append(source_node)
                        node_set.add(key[0])

                    if key[1] not in node_set:
                        target_node = {'id': key[1], 'name': result_sta[key]["name"][1]}
                        node_list.append(target_node)
                        node_set.add(key[1])

        # 标记节点属性，如果为节点自身，标记为1，如果节点在敏感库内，标记为2，其他标记为3
        node_set.remove(uid)
        contain_result = Figure.objects.filter(uid__in=list(node_set)).values()
        contain_set = set([item["uid"] for item in contain_result])
        for node in node_list:
            if node["id"] == uid:
                node["contain_status"] = 1
            elif node["id"] in contain_set:
                node["contain_status"] = 2
            else:
                node["contain_status"] = 3

        social_contact = {
            'node': node_list, 
            'link': link_list, 
            'max_num': max_num, 
            'min_num': min_num
        }

        return JsonResponse(social_contact, safe=False)

# 社交特征阉割版功能接口
class Show_contact(APIView):
    def get(self,request):
        uid = request.GET.get("uid")
        date_window = int(request.GET.get("date_window", 30))
        min_count = int(request.GET.get("min_count", 1))
        max_count = int(request.GET.get("max_count", 9999999999))

        message_type_dic = {
            2: "评论",
            3: "转发"
        }
        # 时间范围内的数据获取，该用户上游和下游的节点连接
        try:
            end_date = Event.objects.filter(figure__uid=uid).order_by('end_date')[0].end_date.strftime('%Y-%m-%d')
        except:
            end_date = today()
        end_ts = date2ts(end_date)
        start_ts = end_ts - date_window * 86400

        result = UserSocialContact.objects.filter((Q(source=uid) | Q(target=uid)) & Q(timestamp__gte=start_ts) & Q(timestamp__lte=end_ts)).values()
        # return JsonResponse({1:list(result)}, safe=False)

        # 对用户多日的数据进行聚合
        result_sta = {}
        for item in result:
            key = (item['source'], item['target'])
            source_name = item['source_name'] if item['source_name'] else item['source']
            target_name = item['target_name'] if item['target_name'] else item['target']
            if key not in result_sta:
                result_sta[key] = {
                    "message_type":{
                        2: 0,
                        3: 0
                    },
                    "name": (source_name, target_name)
                }
            result_sta[key]["message_type"][item['message_type']] += item["count"]

        if len(result_sta) == 0:
            social_contact = {
                'node': [], 
                'link': []
            }
            return JsonResponse(social_contact, safe=False)

        # 形成节点、边的列表，展示节点和边的属性
        node_list = []
        link_list = []
        max_num = 0
        min_num = 9999999999
        node_set = set([])
        for key in result_sta:
            # 去掉自环节点
            if key[0] == key[1]:
                continue

            for message_type in result_sta[key]["message_type"]:
                count = result_sta[key]["message_type"][message_type]
                if count:
                    max_num = max(count, max_num)
                    min_num = min(count, min_num)
                if count >= min_count and count <= max_count:
                    node_link = {
                        'source': result_sta[key]["name"][0],
                        'target': result_sta[key]["name"][1],
                        'value': message_type_dic[message_type]
                    }
                    link_list.append(node_link)

                    if key[0] not in node_set:
                        source_node = {'id': key[0], 'name': result_sta[key]["name"][0]}
                        node_list.append(source_node)
                        node_set.add(key[0])

                    if key[1] not in node_set:
                        target_node = {'id': key[1], 'name': result_sta[key]["name"][1]}
                        node_list.append(target_node)
                        node_set.add(key[1])

        # 限制整体返回的数量，防止画图卡顿
        link_list = sorted(link_list,key=lambda x:x["value"],reverse=True)[:100]
        retrict_node_set = []
        for node_link in link_list:
            retrict_node_set.append(node_link["source"])
            retrict_node_set.append(node_link["target"])
        retrict_node_set = set(retrict_node_set)
        # return JsonResponse({"s":str(retrict_node_set)}, safe=False)

        # 标记节点属性，如果为节点自身，标记为1，如果节点在敏感库内，标记为2，其他标记为3
        node_set.remove(uid)
        contain_result = Figure.objects.filter(uid__in=list(node_set)).values()
        contain_set = set([item["uid"] for item in contain_result])
        node_list_new = []
        for node in node_list:
            if node["name"] not in retrict_node_set:
                continue
            if node["id"] == uid:
                node["value"] = 1
            elif node["id"] in contain_set:
                node["value"] = 2
            else:
                node["value"] = 3
            node.pop("id")
            node_list_new.append(node)

        social_contact = {
            'node': node_list_new, 
            'link': link_list
        }

        return JsonResponse(social_contact, safe=False)



class Figure_create(APIView):
    """添加人物入库"""
    def get(self,request):
        """添加人物：获取添加信息，输入uid,nick,location,fans,friends,political,domain
           调取人物id、昵称、注册地、粉丝数、关注数、政治倾向和领域，若没有填写微博ID则wb_id="";输出状态及提示：400 状态错误，201写入成功"""
        times = int(time.time())
        dates = datetime.datetime.now().strftime('%Y-%m-%d')  # 获取当前时间戳和日期
        f_id = request.GET.get("uid") #f_id与uid均为输入的用户id
        uid = request.GET.get("uid")  
        nick = request.GET.get("nick")
        location = request.GET.get("location")
        fans = request.GET.get("fans")
        friends = request.GET.get("friends")
        political = request.GET.get("political")
        domain = request.GET.get("domain")
        birth = request.GET.get("birthday")
        create_at = request.GET.get("create_at")
        #h_id = request.GET.get("wb_id")  # 若该条人工输入事件从微博而来 则需输入来源微博的id
        #result = Task.objects.filter(~Q(mid=''), mid=h_id) #判断从微博得来的事件是否已存在，若微博ID未给出返回一个空值
        result = Figure.objects.filter(f_id=uid)
        if result.exists():
            return JsonResponse({"status":400, "error": "人物已存在"},safe=False,json_dumps_params={'ensure_ascii':False})
        if f_id :
            if not birth:
                birthday = '未知'
            if not create_at:
                create_at = '未知'
            if not fans:
                fans = '未知'
            if not friends:
                friends = '未知'
            Figure.objects.create(f_id=f_id, uid=uid, nick_name=nick,user_location=location,fansnum=fans,user_birth = birth,create_at=create_at,
                                friendsnum=friends,political = political,domain=domain,computestatus=0)
            return JsonResponse({"status":201, "msg": "人物添加成功"},safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "请输入人物的相关信息"},safe=False,json_dumps_params={'ensure_ascii':False})


class Figure_delete(APIView):
# 选中要删除的人物 选中时传入uid 
    def get(self,request):
        uid = request.GET.get("uid")
        result = Figure.objects.filter(f_id=uid)
        if result.exists():
            try:
                Figure.objects.filter(f_id=uid).delete() 
                return JsonResponse({"status":201, "msg": "人物已删除"},safe=False,json_dumps_params={'ensure_ascii':False})
            except:
                return JsonResponse({"status":400, "error": "删除失败"},safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "人物不存在"},safe=False,json_dumps_params={'ensure_ascii':False})



class Show_figure(APIView):
    """展示人物列表"""
    def get(self, request):
        """展示人物,该文档返回Figure表中存在的需要展示的数据，返回字段f_id为用户账号，nick_name为昵称
          fansnum粉丝数,friendsnum关注数,event_count为参与事件数，info_count为敏感信息数,user_location地点"""
        #result = Figure.objects.all()  #values("f_id","nick_name","fansnum",'friendsnum','political','domain','user_location')
        limit = request.GET.get("limit")
        page_id = request.GET.get('page_id')
        if page_id is None:
            page_id = 1
        if limit is None:
            limit = 10
        results = Figure.objects.filter(computestatus=2,identitystatus=1).order_by('-monitorstatus','-info_count','-event_count')  #,.annotate(Count('event'))filter=(information.uid=f_id)
        #print(results)

        count = len(results)
        result = results[int(limit)*(int(page_id)-1):int(limit)*int(page_id)]
        res_list = []
        if results.exists():
            for item in result:
                fid = item.f_id
                #event_count = 0
                #info_count = 0
                #sdate = item.begin_date.strftime('%Y-%m-%d %H:%M:%S')
                #edate = item.end_date.strftime('%Y-%m-%d %H:%M:%S')
                if item.nick_name is None:
                    nick = fid
                else:
                    nick = item.nick_name
                if item.fansnum is None:
                    fans = "未知"
                else:
                    fans = item.fansnum
                if item.friendsnum is None:
                    friends = "未知"
                else:
                    friends = item.friendsnum
                if item.create_at is None:
                    create_date = "未知"
                else:
                    create_date = item.create_at
                if item.user_location is None:
                    addr = "未知"
                else:
                    addr = item.user_location
                
                #event_count = Figure.objects.get(f_id=fid).event.all().count()
                #info_count = Information.objects.filter(uid=fid).count()
                res_list.append({"f_id":fid,"nick_name":nick,"fansnum":fans,'friendsnum':friends,'create_at':create_date,'event_count':item.event_count,'info_count':item.info_count,'user_location':addr,'count':count})
            return JsonResponse(res_list,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "无人物"},safe=False)



class Show_figure_sort(APIView):
    """展示人物列表"""
    def get(self, request):
        """展示人物,该文档返回Figure表中存在的需要展示的数据，返回字段f_id为用户账号，nick_name为昵称
          fansnum粉丝数,friendsnum关注数,event_count为参与事件数，info_count为敏感信息数,user_location地点"""
        #result = Figure.objects.all()  #values("f_id","nick_name","fansnum",'friendsnum','political','domain','user_location')
        limit = request.GET.get("limit")
        page_id = request.GET.get('page_id')
        name = request.GET.get('label')
        order = request.GET.get('order')
        if page_id is None:
            page_id = 1
        if limit is None:
            limit = 10
        if name == "info_count":
            if order == "descending":
                results = Figure.objects.filter(computestatus=2,identitystatus=1).order_by('-monitorstatus','-info_count','-event_count')
            else:
                results = Figure.objects.filter(computestatus=2,identitystatus=1).order_by('-monitorstatus','info_count','event_count')
        if name == "event_count":
            if order == "descending":
                results = Figure.objects.filter(computestatus=2,identitystatus=1).order_by('-monitorstatus','-event_count','-info_count')
            else:
                results = Figure.objects.filter(computestatus=2,identitystatus=1).order_by('-monitorstatus','event_count','info_count')  #,.annotate(Count('event'))filter=(information.uid=f_id)
        #print(results)

        count = len(results)
        result = results[int(limit)*(int(page_id)-1):int(limit)*int(page_id)]
        res_list = []
        if results.exists():
            for item in result:
                fid = item.f_id
                #event_count = 0
                #info_count = 0
                #sdate = item.begin_date.strftime('%Y-%m-%d %H:%M:%S')
                #edate = item.end_date.strftime('%Y-%m-%d %H:%M:%S')
                if item.nick_name is None:
                    nick = fid
                else:
                    nick = item.nick_name
                if item.fansnum is None:
                    fans = "未知"
                else:
                    fans = item.fansnum
                if item.friendsnum is None:
                    friends = "未知"
                else:
                    friends = item.friendsnum
                if item.create_at is None:
                    create_date = "未知"
                else:
                    create_date = item.create_at
                if item.user_location is None:
                    addr = "未知"
                else:
                    addr = item.user_location
                
                #event_count = Figure.objects.get(f_id=fid).event.all().count()
                #info_count = Information.objects.filter(uid=fid).count()
                res_list.append({"f_id":fid,"nick_name":nick,"fansnum":fans,'friendsnum':friends,'create_at':create_date,'event_count':item.event_count,'info_count':item.info_count,'user_location':addr,'count':count})
            return JsonResponse(res_list,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "无人物"},safe=False)






class search_figure(APIView):
    """展示所搜寻人物信息"""
    def get(self, request):
        """展示人物,该文档返回Figure表中存在的需要展示的数据，返回字段f_id为用户账号，nick_name为昵称
          fansnum粉丝数,friendsnum关注数,political政治倾向,domain领域,user_location地点"""
        info = request.GET.get("info")
        res_list = []
        limit = request.GET.get("limit")
        page_id = request.GET.get('page_id')
        if page_id is None:
            page_id = 1
        if limit is None:
            limit = 10
        result = Figure.objects.filter(Q(nick_name__contains = info) | Q(uid__startswith = info),computestatus=2,identitystatus=1).order_by('-monitorstatus','-info_count')[int(limit)*(int(page_id)-1):int(limit)*int(page_id)]  #.values("f_id","nick_name","fansnum",'friendsnum','political','domain','user_location')
        count = len(Figure.objects.filter(Q(nick_name__contains = info) | Q(uid__startswith = info),computestatus=2,identitystatus=1))
        res_list = []
        if result.exists():
            for item in result:
                #event_count = 0
                #info_count = 0
                #sdate = item.begin_date.strftime('%Y-%m-%d %H:%M:%S')
                #edate = item.end_date.strftime('%Y-%m-%d %H:%M:%S')
                fid = item.f_id
                if item.nick_name is None:
                    nick = fid
                else:
                    nick = item.nick_name
                if item.fansnum is None:
                    fans = "未知"
                else:
                    fans = item.fansnum
                if item.friendsnum is None:
                    friends = "未知"
                else:
                    friends = item.friendsnum
                if item.create_at is None:
                    create_date = "未知"
                else:
                    create_date = item.create_at
                if item.user_location is None:
                    addr = "未知"
                else:
                    addr = item.user_location
                
                #event_count = Figure.objects.get(f_id=fid).event.all().count()
                #info_count = Information.objects.filter(uid=fid).count()
                res_list.append({"f_id":fid,"nick_name":nick,"fansnum":fans,'friendsnum':friends,'create_at':create_date,'event_count':item.event_count,'info_count':item.info_count,'user_location':addr,'count':count})
            res=sorted(res_list,key=operator.itemgetter('info_count'),reverse=True)
            return JsonResponse(res,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "该人物不存在"},safe=False,json_dumps_params={'ensure_ascii':False})




class search_figure_sort(APIView):
    """展示所搜寻人物信息"""
    def get(self, request):
        """展示人物,该文档返回Figure表中存在的需要展示的数据，返回字段f_id为用户账号，nick_name为昵称
          fansnum粉丝数,friendsnum关注数,political政治倾向,domain领域,user_location地点"""
        info = request.GET.get("info")
        res_list = []
        limit = request.GET.get("limit")
        page_id = request.GET.get('page_id')
        name = request.GET.get('label')
        order = request.GET.get('order')
        if page_id is None:
            page_id = 1
        if limit is None:
            limit = 10
        if name == "info_count":
            if order == "descending":
                result = Figure.objects.filter(Q(nick_name__contains = info) | Q(uid__startswith = info),computestatus=2,identitystatus=1).order_by('-monitorstatus','-info_count','-event_count')[int(limit)*(int(page_id)-1):int(limit)*int(page_id)]  #.values("f_id","nick_name","fansnum",'friendsnum','political','domain','user_location')
            else:
                result = Figure.objects.filter(Q(nick_name__contains = info) | Q(uid__startswith = info),computestatus=2,identitystatus=1).order_by('-monitorstatus','info_count','event_count')[int(limit)*(int(page_id)-1):int(limit)*int(page_id)]
        if name == "event_count":
            if order == "descending":
                result = Figure.objects.filter(Q(nick_name__contains = info) | Q(uid__startswith = info),computestatus=2,identitystatus=1).order_by('-monitorstatus','-event_count','-info_count')[int(limit)*(int(page_id)-1):int(limit)*int(page_id)]  #.values("f_id","nick_name","fansnum",'friendsnum','political','domain','user_location')
            else:
                result = Figure.objects.filter(Q(nick_name__contains = info) | Q(uid__startswith = info),computestatus=2,identitystatus=1).order_by('-monitorstatus','event_count','info_count')[int(limit)*(int(page_id)-1):int(limit)*int(page_id)]

        count = len(Figure.objects.filter(Q(nick_name__contains = info) | Q(uid__startswith = info),computestatus=2,identitystatus=1))
        res_list = []
        if result.exists():
            for item in result:
                #event_count = 0
                #info_count = 0
                #sdate = item.begin_date.strftime('%Y-%m-%d %H:%M:%S')
                #edate = item.end_date.strftime('%Y-%m-%d %H:%M:%S')
                fid = item.f_id
                if item.nick_name is None:
                    nick = fid
                else:
                    nick = item.nick_name
                if item.fansnum is None:
                    fans = "未知"
                else:
                    fans = item.fansnum
                if item.friendsnum is None:
                    friends = "未知"
                else:
                    friends = item.friendsnum
                if item.create_at is None:
                    create_date = "未知"
                else:
                    create_date = item.create_at
                if item.user_location is None:
                    addr = "未知"
                else:
                    addr = item.user_location
                
                #event_count = Figure.objects.get(f_id=fid).event.all().count()
                #info_count = Information.objects.filter(uid=fid).count()
                res_list.append({"f_id":fid,"nick_name":nick,"fansnum":fans,'friendsnum':friends,'create_at':create_date,'event_count':item.event_count,'info_count':item.info_count,'user_location':addr,'count':count})
            res=sorted(res_list,key=operator.itemgetter('info_count'),reverse=True)
            return JsonResponse(res,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "该人物不存在"},safe=False,json_dumps_params={'ensure_ascii':False})




class show_figure_info(APIView):
    """展示人物详细信息"""
    def get(self,request):
        """获取uid 返回返回字段f_id为用户账号，nick_name为昵称,event_count为参与事件数，info_count为敏感信息数
          fansnum粉丝数,friendsnum关注数,political政治倾向,domain领域,user_location地点"""
        event_count = 0
        info_count = 0
        res_dict = {}
        fid = request.GET.get("uid")
        res = Figure.objects.filter(f_id=fid).values("f_id","nick_name","fansnum",'friendsnum','political','domain','user_location','create_at','sex','user_birth','info_count','event_count')
        if res.exists():
            res_event = Figure.objects.get(f_id=fid).event.all()
            #event_count = Figure.objects.get(f_id=fid).event.all().count()
            #info_count = Information.objects.filter(uid=fid).count()
            res_dict["uid"] = fid
            for re in res:
                if re["nick_name"] is None:
                    nick = fid
                else:
                    nick = re["nick_name"]
                if re["fansnum"] is None:
                    fans = "未知"
                else:
                    fans = re["fansnum"]
                if re["friendsnum"] is None:
                    friends = "未知"
                else:
                    friends = re["friendsnum"]
                res_dict["nick_name"]= nick
                res_dict["fansnum"]=fans
                res_dict['friendsnum']=friends
                #print(re["create_at"])
                if re['create_at'] is None:
                    create_date = "未知"
                else:
                    create_date = re['create_at']
                if re['user_location'] is None:
                    addr = "未知"
                else:
                    addr = re['user_location']
                if re['sex'] is None:
                    sex = '未知'
                else:
                    sex = re['sex']
                if re['user_birth'] is None:
                    age = "未知"
                else:
                    if re['user_birth'] < "1000-00-00":
                        age = "未知"
                    else:
                        age = datetime.date.today().year - int(re['user_birth'][:4])
                res_dict['create_at']=create_date
                res_dict['user_location']=addr
                if re["domain"] is None:
                    domain = "未知"
                else:
                    domain = domain_dict[re["domain"]]
                if re["political"] is None:
                    political = "未知"
                else:
                    political = political_dict[re["political"]]
                res_dict["domain"]=domain
                res_dict["political"]=political
                res_dict['age'] = age
                res_dict['sex'] = sex
            res_dict['event_count']=re['event_count']
            res_dict['info_count']=re['info_count']
            return JsonResponse(res_dict,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "无人物"},safe=False)


class show_cal_figure(APIView):
    """展示人物计算任务"""
    def get(self, request):
        jre = []
        result = Figure.objects.filter(identitystatus=1,computestatus__in=[0,1]).values('f_id','nick_name','into_date','computestatus').order_by('-computestatus','-into_date')
        if result.exists():
            for item in result:
                #sdate = item['into_date'].strftime('%Y-%m-%d')
                if item['into_date'] is None:
                    sdate = datetime.date.today()
                else:
                    sdate = item['into_date'].strftime('%Y-%m-%d')
                if item['nick_name'] is None:
                    nick = item['f_id']
                else:
                    nick = item['nick_name']
                jre.append({"fid":item["f_id"],"nick_name":nick,"cal_status":item['computestatus'],\
                                "into_date":sdate})
            return JsonResponse(jre,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "人物任务不存在"},safe=False,json_dumps_params={'ensure_ascii':False})




class delete_cal_figure(APIView):
    """删除人物计算任务"""
    def get(self, request):
        fid = request.GET.get("fid")
        result = Figure.objects.filter(f_id=fid)
        if result.exists():
            try:
                Figure.objects.filter(f_id=fid).delete() 
                return JsonResponse({"status":201, "msg": "计算任务已删除"},safe=False,json_dumps_params={'ensure_ascii':False})
            except:
                return JsonResponse({"status":400, "error": "删除失败"},safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "人物不存在"},safe=False,json_dumps_params={'ensure_ascii':False})





class related_info(APIView):
    """人物-信息关联分析"""
    def get(self,request):
        res_dict = defaultdict(list)
        fid = request.GET.get('uid')
        limit = request.GET.get("limit")
        page_id = request.GET.get('page_id')
        if page_id is None:
            page_id = 1
        if limit is None:
            limit = 10
        res = Information.objects.filter(uid=fid,cal_status=2).order_by('-timestamp')[int(limit)*(int(page_id)-1):int(limit)*int(page_id)]
        count = len(Information.objects.filter(uid=fid,cal_status=2))
        res_dict['count'] = count
        #print(len(res))
        if res.exists():
            for i in res:
                lt = time.localtime(i.timestamp)
                itime = time.strftime('%Y-%m-%d %H:%M:%S',lt)
                #print(itime)
                res_dict['table'].append(['text','time','geo','id'])
                res_dict['data'].append([i.text,itime,i.geo,i.i_id])
            '''
            page = Paginator(res_dict, limit)
            #page_id = request.GET.get('page_id')
            if page_id:
                try:
                    results = page.page(page_id)
                except PageNotAnInteger:
                    results = page.page(1)
                except EmptyPage:
                    results = page.page(1)
            else:
                results = page.page(1)
            re = json.dumps(list(results),ensure_ascii=False)
            re = json.loads(re)
            '''
            return JsonResponse(res_dict,safe=False,json_dumps_params={'ensure_ascii':False}) #
        else:
            return JsonResponse({"status":400, "error": "无相关信息"},safe=False)



class related_event(APIView):
    """人物-事件相关信息"""
    def get(self,request):
        res_dict = defaultdict(list)
        fid = request.GET.get('uid')
        limit = request.GET.get("limit")
        page_id = request.GET.get('page_id')
        if page_id is None:
            page_id = 1
        if limit is None:
            limit = 10
        res = Figure.objects.filter(uid=fid)
        if res.exists():
            res_event = Figure.objects.get(f_id=fid).event.all().filter(~Q(hidden_status=1),cal_status=2).order_by('-begin_date')[int(limit)*(int(page_id)-1):int(limit)*int(page_id)]
            count = len(Figure.objects.get(f_id=fid).event.all().filter(~Q(hidden_status=1),cal_status=2))
            res_dict['count'] = count
            for e in res_event:
                #lt = time.localtime(i.timestamp)
                #itime = time.strftime('%Y-%m-%d %H:%M:%S',lt)
                #print(itime)
                sdate = e.begin_date.strftime('%Y-%m-%d')
                if e.end_date is None:
                    edate = '至今'
                else:
                    edate = e.end_date.strftime('%Y-%m-%d')
                res_dict['table'].append(['event_name','keywords','begin_date','end_date','id'])
                res_dict['data'].append([e.event_name,e.keywords_dict,sdate,edate,e.e_id])
            '''
            page = Paginator(res_dict, limit)
            #page_id = request.GET.get('page_id')
            if page_id:
                try:
                    results = page.page(page_id)
                except PageNotAnInteger:
                    results = page.page(1)
                except EmptyPage:
                    results = page.page(1)
            else:
                results = page.page(1)
            re = json.dumps(list(results),ensure_ascii=False)
            re = json.loads(re)
            '''
            return JsonResponse(res_dict,safe=False,json_dumps_params={'ensure_ascii':False}) #
        else:
            return JsonResponse({"status":400, "error": "无相关事件"},safe=False)






class User_Sentiment(APIView):
    """用户情绪特征接口"""

    def get(self, request):
        """
        获取uid，返回用户情绪特征详情，根据传入参数n_type 日 周 月 返回相应数据结果，
        返回数据格式{date1:{positive_s:10,nuetral_s:20,negtive_s:30},
                    date2:{positive_s:10,nuetral_s:20,negtive_s:30},
                    ...}
        """
        uid = request.GET.get('uid')
        n_type = request.GET.get('n_type')
        try:
            date = UserSentiment.objects.filter(uid=uid).order_by('-store_date')[0].store_date.strftime('%Y-%m-%d')
        except:
            date = today()
        res_dict = defaultdict(dict)
        date = date2ts(date)
        # 每日情绪特征，从当前日期往前推7天展示 积极微博数，中性微博数，消极微博数
        if n_type == "日":
            dl = get_datelist_v2(ts2date(date - 149 * 86400),ts2date(date))
            # result = UserSentiment.objects.filter(uid=uid, timestamp__gte=date2ts(dl[0]), timestamp__lte=date).values("store_date").annotate(positive_s=Sum("positive"), nuetral_s=Sum("nuetral"), negtive_s=Sum("negtive"))
            # for d in dl:
            #     r = {}
            #     for i in result:
            #         if d == str(i['store_date']):
            #             r = i
            for d in dl:
                result = UserSentiment.objects.filter(uid=uid, store_date__gte=d, store_date__lte=d).values('positive','nuetral','negtive')
                if result.exists():
                    res_dict['positive'][d] = result[0]['positive']
                    res_dict['nuetral'][d] = result[0]['nuetral']
                    res_dict['negtive'][d] = result[0]['negtive']
                else:
                    res_dict['positive'][d] = 0
                    res_dict['nuetral'][d] = 0
                    res_dict['negtive'][d] = 0
        # 每周情绪特征，从当前日期往前推5周展示 积极微博数，中性微博数，消极微博数
        if n_type == "周":
            date_dict = {}
            for i in range(1,23):
                date_dict[i] = (datetime.datetime.strptime(ts2date(date), '%Y-%m-%d') + datetime.timedelta(weeks=(-1 * i))).timestamp()
            date_dict[0] = date
            for i in [21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4, 3, 2, 1, 0]:
                result = UserSentiment.objects.filter(uid=uid, timestamp__gt=date_dict[i + 1],
                                                     timestamp__lte=date_dict[i]).aggregate(
                    positive_s=Sum("positive"), nuetral_s=Sum("nuetral"), negtive_s=Sum("negtive"))
                if result['positive_s'] != None:
                    res_dict['positive'][ts2date(date_dict[i])] = result['positive_s']
                    res_dict['nuetral'][ts2date(date_dict[i])] = result['nuetral_s']
                    res_dict['negtive'][ts2date(date_dict[i])] = result['negtive_s']
                else:
                    res_dict['positive'][ts2date(date_dict[i])] = 0
                    res_dict['nuetral'][ts2date(date_dict[i])] = 0
                    res_dict['negtive'][ts2date(date_dict[i])] = 0
        # 每月情绪特征，从当前日期往前推5月展示 积极微博数，中性微博数，消极微博数
        if n_type == "月":
            date_dict = {}
            for i in range(1,6):
                date_dict[i] = (datetime.datetime.strptime(ts2date(date), '%Y-%m-%d') + datetime.timedelta(days=(-30 * i))).timestamp()
            date_dict[0] = date
            for i in [4, 3, 2, 1, 0]:
                result = UserSentiment.objects.filter(uid=uid, timestamp__gt=date_dict[i + 1],
                                                     timestamp__lte=date_dict[i]).aggregate(
                    positive_s=Sum("positive"), nuetral_s=Sum("nuetral"), negtive_s=Sum("negtive"))
                if result['positive_s'] != None:
                    res_dict['positive'][time.strftime("%Y-%m", time.localtime(date_dict[i]))] = result['positive_s']
                    res_dict['nuetral'][time.strftime("%Y-%m", time.localtime(date_dict[i]))] = result['nuetral_s']
                    res_dict['negtive'][time.strftime("%Y-%m", time.localtime(date_dict[i]))] = result['negtive_s']
                else:
                    res_dict['positive'][time.strftime("%Y-%m", time.localtime(date_dict[i]))] = 0
                    res_dict['nuetral'][time.strftime("%Y-%m", time.localtime(date_dict[i]))] = 0
                    res_dict['negtive'][time.strftime("%Y-%m", time.localtime(date_dict[i]))] = 0
        n_res = defaultdict(dict)
        n_res['date'] = list(res_dict['positive'].keys())
        n_res['positive_num'] = list(res_dict['positive'].values())
        n_res['nuetral_num'] = list(res_dict['nuetral'].values())
        n_res['negtive_num'] = list(res_dict['negtive'].values())
        return JsonResponse(n_res)



class User_Influence(APIView):
    """用户影响力特征接口"""

    def get(self, request):
        """
        获取uid，返回用户影响力特征详情，根据传入参数n_type 日 周 月 返回相应数据结果，
        返回数据格式{date1:{positive_s:10,nuetral_s:20,negtive_s:30},
                    date2:{positive_s:10,nuetral_s:20,negtive_s:30},
                    ...}
        """
        uid = request.GET.get('uid')
        n_type = request.GET.get('n_type')
        try:
            date = NewUserInfluence.objects.filter(uid=uid).exclude(influence=0).order_by('-store_date')[0].store_date.strftime('%Y-%m-%d')
        except:
            date = today()
        res_dict = defaultdict(dict)
        date = date2ts(date)
        # 每日影响力特征，从当前日期往前推7天展示 影响力 活跃度 重要度 敏感度
        if n_type == "日":
            dl = get_datelist_v2(ts2date(date - 149 * 86400), ts2date(date))
            # dl = get_datelist_v2(ts2date(date - 6 * 86400), ts2date(date))
            for d in dl:
                result =  NewUserInfluence.objects.filter(uid=uid, store_date__gte=d, store_date__lte=d).values('influence','importance','sensitity','activity')
                if result.exists():
                    res_dict['influence'][d] = result[0]['influence']
                    res_dict['importance'][d] = result[0]['importance']
                    res_dict['sensitity'][d] = result[0]['sensitity']
                    res_dict['activity'][d] = result[0]['activity']
                else:
                    res_dict['influence'][d] = 0
                    res_dict['importance'][d] = 0
                    res_dict['sensitity'][d] = 0
                    res_dict['activity'][d] = 0
        # 每周影响力特征，从当前日期往前推5周展示
        if n_type == "周":
            date_dict = {}
            for i in range(1,23):
                date_dict[i] = (datetime.datetime.strptime(ts2date(date), '%Y-%m-%d') + datetime.timedelta(weeks=(-1 * i))).timestamp()
            # for i in range(1, 6):
            #     date_dict[i] = (datetime.datetime.strptime(ts2date(date), '%Y-%m-%d') + datetime.timedelta(
            #         weeks=(-1 * i))).timestamp()
            date_dict[0] = date
            for i in [21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]:
            # for i in [4, 3, 2, 1, 0]:
                result = NewUserInfluence.objects.filter(uid=uid, timestamp__gte=date_dict[i + 1],
                                                       timestamp__lt=date_dict[i]).aggregate(
                    influence=Avg("influence"), importance=Avg("importance"),
                    sensitity=Avg("sensitity"), activity=Avg("activity"))
                if result['influence'] != None:
                    res_dict['influence'][ts2date(date_dict[i])] = result['influence']
                    res_dict['importance'][ts2date(date_dict[i])] = result['importance']
                    res_dict['sensitity'][ts2date(date_dict[i])] = result['sensitity']
                    res_dict['activity'][ts2date(date_dict[i])] = result['activity']
                else:
                    res_dict['influence'][ts2date(date_dict[i])] = 0
                    res_dict['importance'][ts2date(date_dict[i])] = 0
                    res_dict['sensitity'][ts2date(date_dict[i])] = 0
                    res_dict['activity'][ts2date(date_dict[i])] = 0
        # 每月情绪特征，从当前日期往前推5月展示
        if n_type == "月":
            date_dict = {}
            # for i in range(1, 6):
            #     date_dict[i] = (datetime.datetime.strptime(ts2date(date), '%Y-%m-%d') + datetime.timedelta(
            #         days=(-30 * i))).timestamp()
            # date_dict[0] = date
            for i in range(1,6):
                date_dict[i] = (datetime.datetime.strptime(ts2date(date), '%Y-%m-%d') + datetime.timedelta(days=(-30 * i))).timestamp()
            date_dict[0] = date
            for i in [4, 3, 2, 1, 0]:
                result = NewUserInfluence.objects.filter(uid=uid, timestamp__gte=date_dict[i + 1],
                                                         timestamp__lt=date_dict[i]).aggregate(
                    influence=Avg("influence"), importance=Avg("importance"),
                    sensitity=Avg("sensitity"), activity=Avg("activity"))
                if result['influence'] != None:
                    res_dict['influence'][ts2date(date_dict[i])] = result['influence']
                    res_dict['importance'][ts2date(date_dict[i])] = result['importance']
                    res_dict['sensitity'][ts2date(date_dict[i])] = result['sensitity']
                    res_dict['activity'][ts2date(date_dict[i])] = result['activity']
                else:
                    res_dict['influence'][ts2date(date_dict[i])] = 0
                    res_dict['importance'][ts2date(date_dict[i])] = 0
                    res_dict['sensitity'][ts2date(date_dict[i])] = 0
                    res_dict['activity'][ts2date(date_dict[i])] = 0
        n_res = defaultdict(dict)
        n_res['date'] = list(res_dict['influence'].keys())
        n_res['influence_num'] = list(res_dict['influence'].values())
        n_res['importance_num'] = list(res_dict['importance'].values())
        n_res['sensitity_num'] = list(res_dict['sensitity'].values())
        n_res['activity_num'] = list(res_dict['activity'].values())
        return JsonResponse(n_res)