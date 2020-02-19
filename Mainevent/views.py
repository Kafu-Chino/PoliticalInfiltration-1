# -*- coding: utf-8 -*-
import json
import time,datetime
from xpinyin import Pinyin
from collections import defaultdict
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.db.models import Q

from Config.time_utils import *
from Mainevent.models import Event_Analyze, Event, Figure, Information
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Systemmanage.models import SensitiveWord
from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema

class Show_event(APIView):
    """展示事件列表
       输出{‘event_name(事件名称)’: ,’keywords_dict(事件关键词)’: ,’content(事件内容)’: , ‘begin_date(开始日期)’:  ,‘end_date(结束日期)’: },{},{}"""
    def get(self, request):
        result = Event.objects.values('e_id','event_name','keywords_dict','begin_date','end_date')
        limit = request.GET.get("limit")
        page_id = request.GET.get('page_id')
        index_list = {}
        jre=[]
        #t1 = time.time()
        if result.exists():
            for item in result:
                sdate = item.begin_date.strftime('%Y-%m-%d %H:%M:%S')
                edate = item.end_date.strftime('%Y-%m-%d %H:%M:%S')
                eid = item.e_id
                e_re = Event.objects.filter(e_id =eid)
                figure_count = len(e_re.figure.all())
                info_count = len(e_re.information.all())
                all_re = Event_Analyze.objects.filter(e_id =eid).values('weibo_count','user_count')
                for re in all_re:
                    weibo_count = re['weibo_count']
                    user_count = re['user_count']
                '''
                index_name = item.index_name
                if index_name in index_list:
                    weibo_count = index_list[index_name]['weibo_count']
                    user_count = index_list[index_name]['user_count']
                else:
                    query_body = {
                            "query": {
                            "match_all":{}
                                 }
                             }
                    r = scan(es, index=index_name, query=query_body)
                    weibo_count = 0
                    user_list =[]
                    user_count = 0
                    for item in r:
                        weibo_count += 1
                        if item['_source']["uid"] in user_list:
                            continue
                        else:
                            user_count += 1
                            user_list.append(item['_source']["uid"])
                '''
                jre.append({"event_name":item.event_name,"keywords_dict":keywords_dict,"begin_date":sdate,'end_date':edate,'sensitive_figure_ratio':figure_count/user_count,'sensitive_info_ratio':info_count/weibo_count})
            #t2 = time.time()
            #print(t2-t1)
            #jre = json.dumps(list(result))
            #jre = list(result)
            page = Paginator(jre, limit)
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
            '''
            pageData = serializers.serialize("json", results)
            pageData = json.loads(pageData, encoding='utf-8')
            jre['result']=pageData
            '''
            re = json.dumps(list(results),ensure_ascii=False)
            
            #print(type(re))
            #json_data2 = serializers.serialize("json",results)
            results2 = json.loads(re)
            return JsonResponse(results2,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "无事件"},safe=False)



class Show_event_info(APIView):
    """展示事件详情,点击事件传入事件eid
       输出{‘event_name(事件名称)’: ,’keywords_dict(事件关键词)’: ,’content(事件内容)’: , ‘begin_date(开始日期)’:  ,‘end_date(结束日期)’: },{},{}"""
    def get(self, request):
        eid = request.GET.get("eid")
        result = Event.objects.filter(e_id =eid)
        jre = []
        if result.exists():
            for item in result:
                figure_count = len(item.figure.all())
                info_count = len(item.information.all())
                all_re = Event_Analyze.objects.filter(e_id =eid).values('weibo_count','user_count')
                for re in all_re:
                    weibo_count = re['weibo_count']
                    user_count = re['user_count']
                jre.append({"event_name":item.event_name,"keywords_dict":item.keywords_dict,"begin_date":item.begin_date,'end_date':item.end_date,\
                           'user_count':user_count,'weibo_count':weibo_count,'sensitive_figure_ratio':figure_count/user_count,'sensitive_info_ratio':info_count/weibo_count})
            re = json.dumps(jre,ensure_ascii=False)
            return JsonResponse(re,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "无事件详情"},safe=False)


class Add_event(APIView):
    """
    添加新的事件计算任务
    """
    def post(self, request):
        event_name = request.POST.get("event_name")
        keywords_dict = request.POST.get("keywords_dict")
        sensitive_word_white = request.POST.get("sensitive_word_white")
        sensitive_word_black = request.POST.get("sensitive_word_black")
        begin_date = request.POST.get("begin_date")
        end_date = request.POST.get("end_date")

        if not event_name or not keywords_dict:
            return JsonResponse({"status":400, "info": "添加失败，缺少必填项！"},safe=False)

        if not begin_date:
            end_date = today()
        if not begin_date:
            begin_date = ts2date(date2ts(today()) - 19 * 86400)

        event_name_pinyin = Pinyin().get_pinyin(event_name, '')
        e_id = "{}_{}".format(event_name_pinyin, str(int(time.time())))
        Event.objects.create(
            e_id=e_id,
            event_name=event_name,
            keywords_dict=keywords_dict,
            begin_date=begin_date,
            end_date=end_date,
            es_index_name=e_id,
            cal_status=0,
            monitor_status=1
        )

        if sensitive_word_white:
            for word_white in sensitive_word_white.split("&"):
                SensitiveWord.objects.create(
                    s_id=word_white + e_id, 
                    prototype=word_white, 
                    e_id=e_id, 
                    perspective_bias=1
                )

        if sensitive_word_black:
            for word_black in sensitive_word_black.split("&"):
                SensitiveWord.objects.create(
                    s_id=word_black + e_id, 
                    prototype=word_black, 
                    e_id=e_id, 
                    perspective_bias=2
                )

        return JsonResponse({"status":200, "info": "添加成功！"},safe=False)


class Event_trend(APIView):
    """事件热度、敏感度、负面指数
       输入事件id:eid
       输出{"hot_index(热度)": ,"sensitive_index(敏感度)": ,"negative_index(负面指数)":}"""
    def get(self, request):
        """获取事件id:eid"""
        event_id = request.GET.get('eid') 
        res_dict= []
        times = time.time()
        result = Event_Analyze.objects.filter(e_id = event_id)
        if result.exists():
            for re in result:
                res_dict.append({"hot_index":re.hot_index,"sensitive_index":re.sensitive_index,"negative_index":re.negative_index})
            return JsonResponse(res_dict,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "事件不存在"},safe=False,json_dumps_params={'ensure_ascii':False})


class representative_info(APIView):
    """输入事件id:eid 
       输出代表微博列表：[{"uid": ,"comment": ,"retweeted": ,"date": ,"text": ,"hazard": },{}...]"""
    def get(self, request):
        event_id = request.GET.get('eid')
        etime = request.GET.get('time')
        td1 = etime + " 00:00:00"
        ta1 = time.strptime(td1, "%Y-%m-%d %H:%M:%S")
        ts1 = int(time.mktime(ta1))
        td2 = etime + " 23:59:59"
        ta2 = time.strptime(td2, "%Y-%m-%d %H:%M:%S")
        ts2 = int(time.mktime(ta2))
        res = []
        e = Event.objects.filter(e_id = event_id)
        for item in e:
            info = item.information.all().filter(timestamp__range=(ts1,ts2) ).order_by("hazard_index")[:5]
            for i in info:
                lt = time.localtime(i.timestamp)
                itime = time.strftime("%Y-%m-%s %H:%M:%S",lt)
                res.append({"uid":i.uid,"comment":i.comment,"retweeted":i.retweeted,"date":itime,"text":i.text,"hazard":i.hazard_index})
        return JsonResponse(res,safe=False,json_dumps_params={'ensure_ascii':False})


class search_event(APIView):
    """搜索事件 输入事件标题title 输出'event_name','keywords_dict','content','begin_date','end_date'"""
    def get(self, request):
        name = request.GET.get("title")
        result = Event.objects.filter(event_name__contains = name).values('event_name','keywords_dict','content','begin_date','end_date')
        if result.exists():
            re = json.dumps(list(result),ensure_ascii=False)
            re = json.loads(re)
            return JsonResponse(re,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "该事件不存在"},safe=False)

class related_figure(APIView):
    """人物和信息关联分析"""

    def get(self, request):
        """获取事件eid，返回该事件的相关人物和相关信息,
        数据格式{
                    "figure":[{"f_id": uid, "nick_name": nick_name,"fansnum":fansnum,"friendsnum":friendsnum,"domian":domain,"political":political},{}],
                    "information":[{"text": text1, "hazard_index": hazard_index1},{}]
                }
        """
        res_dict = []
        eid = request.GET.get('eid')
        limit = request.GET.get("limit")
        page_id = request.GET.get('page_id')
        res_event = Event.objects.filter(e_id=eid)  #.first().event_set.all()
        for e in res_event:
            #print(e)
            res = e.figure.all()
            for f in res:
                res_dict.append({"f_id": f.f_id, "nick_name": f.nick_name,"fansnum":f.fansnum,"friendsnum":f.friendsnum})
        if len(res_dict):
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
            return JsonResponse(re,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "无相关人物和信息"},safe=False)


class related_info(APIView):
    """人物和信息关联分析"""

    def get(self, request):
        """获取事件eid，返回该事件的相关人物和相关信息,
        数据格式{
                    "figure":[{"f_id": uid, "nick_name": nick_name,"fansnum":fansnum,"friendsnum":friendsnum,"domian":domain,"political":political},{}],
                    "information":[{"text": text1, "hazard_index": hazard_index1},{}]
                }
        """
        res_dict = []
        eid = request.GET.get('eid')
        limit = request.GET.get("limit")
        page_id = request.GET.get('page_id')
        res_event = Event.objects.filter(e_id=eid)  #.first().event_set.all()
        for e in res_event:
            #print(e)
            res1 = e.information.all()
            for i in res1:
                lt = time.localtime(i.timestamp)
                itime = time.strftime('%Y-%m-%d %H:%M:%S',lt)
                #print(itime)
                res_dict.append({'text': i.text,'time':itime,'geo':i.geo})
                #print(res_dict["info"])
        if len(res_dict):
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
            return JsonResponse(re,safe=False,json_dumps_params={'ensure_ascii':False}) #
        else:
            return JsonResponse({"status":400, "error": "无相关人物和信息"},safe=False)


class Person_show(APIView):
    """用户主表展示"""
    def get(self, request):
        """
        用户展示大表信息
        输入：
        pagenum：当前页码数（以1起始）
        pagelimit：每页显示个数
        输出：
        uid：用户id
        nick_name：人物昵称
        create_at：注册时间
        user_location：注册地点
        fansnum：粉丝数
        friendsnum：关注数
        information_num：发布敏感信息数
        events_name：相关渗透事件
        """
        page_num = int(request.GET.get('pagenum', 1)) - 1
        page_limit = int(request.GET.get('pagelimit', 10))
        persons = Figure.objects.all()[page_num * page_limit : (page_num + 1) * page_limit]
        results = []

        # 批量得到用户相关信息统计
        persons_uid = [p.uid for p in persons]
        informations = Information.objects.filter(uid__in=persons_uid)
        information_count = {uid:0 for uid in persons_uid}
        for i in informations:
            information_count[i.uid] += 1

        # 批量得到用户相关事件统计
        events = Event.objects.filter(figure__uid__in=persons_uid).values_list("event_name", "figure__uid")
        events_name = {uid:[] for uid in persons_uid}
        for e in events:
            event_name, uid = e
            events_name[uid].append(event_name)

        for person in persons:
            dic = {
                "uid":person.uid,
                "nick_name":person.nick_name,
                "create_at":ts2date(int(person.create_at)),
                "user_location":person.user_location,
                "fansnum":person.fansnum,
                "friendsnum":person.friendsnum,
                "information_num":information_count[person.uid],
                "events_name":events_name[person.uid]
            }
            results.append(dic)
        return JsonResponse(results, safe=False)
