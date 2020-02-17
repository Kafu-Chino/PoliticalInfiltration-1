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
from Systemmanage.models import SensitiveWord

from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema

class Show_event(APIView):
    """展示事件列表
       输出{‘event_name(事件名称)’: ,’keywords_dict(事件关键词)’: ,’content(事件内容)’: , ‘begin_date(开始日期)’:  ,‘end_date(结束日期)’: },{},{}"""
    def get(self, request):
        result = Event.objects.values('event_name','keywords_dict','content','begin_date','end_date')
        if result.exists():
            return HttpResponse(result)
        else:
            return JsonResponse({"status":400, "error": "无事件"},safe=False)



class Show_event_info(APIView):
    """展示事件详情,点击事件传入事件eid
       输出{‘event_name(事件名称)’: ,’keywords_dict(事件关键词)’: ,’content(事件内容)’: , ‘begin_date(开始日期)’:  ,‘end_date(结束日期)’: },{},{}"""
    def get(self, request):
        eid = request.GET.get("eid")
        result = Event.objects.filter(e_id =eid).values('event_name','keywords_dict','content','begin_date','end_date')
        if result.exists():
            return HttpResponse(result)
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


class Event_analy(APIView):
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
        res = []
        e = Event.objects.filter(e_id = event_id)
        for item in e:
            info = item.information.all().filter(date=etime).order_by("hazard_index")[:5]
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
            return HttpResponse(result)
        else:
            return JsonResponse({"status":400, "error": "该事件不存在"},safe=False)

class figure_info(APIView):
    """人物和信息关联分析"""

    def get(self, request):
        """获取事件eid，返回该事件的相关人物和相关信息,
        数据格式{
                    "figure":[{"f_id": uid, "nick_name": nick_name,"fansnum":fansnum,"friendsnum":friendsnum,"domian":domain,"political":political},{}],
                    "information":[{"text": text1, "hazard_index": hazard_index1},{}]
                }
        """
        res_dict = defaultdict(list)
        eid = request.GET.get('eid')
        res_event = Event.objects.filter(e_id=eid)  #.first().event_set.all()
        for e in res_event:
            res = e.figure.all()
            for f in res:
                res_dict["figure"].append({"f_id": f.f_id, "nick_name": f.nick_name,"fansnum":f.fansnum,"friendsnum":f.friendsnum,"domian":f.domain,"political":f.political})
            #res_dict["figure"].append({"f_id": f.f_id, "nick_name": f.nick_name,"fansnum":f.fansnum,"friendsnum":f.friendsnum,"domian":f.domain,"political":f.political})
        #res_information = Information.objects.filter(e_id=eid)
        #for i in res_information:
            res1 = e.information.all()
            for i in res1:
                res_dict["info"].append({"text": i.text, "hazard_index": i.hazard_index,"keywords":i.keywords_dict,"comment":i.comment,"retweet":i.retweeted})
        if len(res_dict["figure"]) or len(res_dict["info"]):
            return JsonResponse(res_dict,safe=False,json_dumps_params={'ensure_ascii':False})
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
