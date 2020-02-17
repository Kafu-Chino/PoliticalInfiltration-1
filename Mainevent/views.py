# -*- coding: utf-8 -*-
import json
import time,datetime
from collections import defaultdict
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.db.models import Q
from Mainevent.models import Event_Analyze, Event, Figure, Information
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
            re = json.dumps(list(results))
            #print(type(re))
            #json_data2 = serializers.serialize("json",results)
            #results2 = json.loads(json_data2)
            return JsonResponse(re,safe=False,json_dumps_params={'ensure_ascii':False})
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
            re = json.dumps(jre)
            return JsonResponse(re,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "无事件详情"},safe=False)



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
            print(e)
            info = item.information.all() #.filter(timestamp__range=(ts1,ts2) ).order_by("hazard_index")[:5]
            print(info)
        for i in info:
            print(i)

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
            re = json.dumps(list(result))
            return JsonResponse(re,safe=False,json_dumps_params={'ensure_ascii':False})
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
            print(e)
            res = e.figure.all()
            for f in res:
                res_dict["figure"].append({"f_id": f.f_id, "nick_name": f.nick_name,"fansnum":f.fansnum,"friendsnum":f.friendsnum})
            #res_dict["figure"].append({"f_id": f.f_id, "nick_name": f.nick_name,"fansnum":f.fansnum,"friendsnum":f.friendsnum,"domian":f.domain,"political":f.political})
        #res_information = Information.objects.filter(e_id=eid)
        #for i in res_information:
            res1 = e.information.all()
            for i in res1:
                lt = time.localtime(i.timestamp)
                itime = time.strftime("%Y-%m-%s %H:%M:%S",lt)
                res_dict["info"].append({"text": i.text,"time":itime,"geo":i.geo})
        if len(res_dict["figure"]) or len(res_dict["info"]):
            return JsonResponse(res_dict,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "无相关人物和信息"},safe=False)



import os
import sys
import re
ABS_PATH = os.path.dirname(os.path.abspath(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'
class Sen_info(APIView):
    """展示敏感微博内容涉及到的敏感词
       输入：敏感微博id：id
       输出：{‘sw(敏感词汇)’:{},…, ‘info’:{‘text’(敏感信息内容)：，‘hazard_index(危险指数)’：，‘keywords(关键词)’: , ‘comment(评论数)’：，‘retweet(转发数)’：}}"""
    def get(self,request):
        swords = []
        for b in open(os.path.abspath(os.path.join(ABS_PATH, '../Cron/profile_cal/sensitive_words.txt')), 'r'):
            swords.append(b.strip().split('\t')[0])
        iid = request.GET.get('id')
        result = Information.objects.filter(i_id=iid).values("uid",'text','keywords_dict','comment','retweeted','date','hazard_index')
        res = defaultdict(list)
        #results = json.dumps(result)
        for i in result:
            for word in swords:
            #print(type(word))
                pattern = re.compile(r".*(%s)" % word)
                if pattern.search(i['text']): 
                    res["sw"].append(word)
            res["info"].append(i)
        #json_data = serializers.serialize("json",result)
        #results = json.loads(json_data)
        return JsonResponse(res,safe=False,json_dumps_params={'ensure_ascii':False})



class push_Hotpost(APIView):
    """页面响应,从数据库取热帖展示"""
    def get(self):
        hot_posts = Hot_post.objects.all().values_list()  # 取出所有列，QuerySet类型
        hot_posts = list(hot_posts)  # [(data),(data)]
        # 元组(data):
        # (h_id, uid, root_uid, mid, comment, retweeted, text, keywords_dict, timestamp, date, ip, geo, message_type, root_mid, source, store_timestamp, store_date, similar_event)
        # 例如:
        # ('h_1', 'user_1', 'user_1', 'm_1', 0, 0, '测试热帖库信息', 't1,t2,t3,t4,t5', 1567923180, datetime.date(2019, 9, 8), '127.0.0.1', '北京市', 1, 'm_1', '微博', 1567925639, datetime.date(2019, 9, 8), None)
        hot_post_display = []
        for item in hot_posts:
            a_post = {}
            a_post["h_id"] = item[0]
            a_post["uid"] = item[1]
            a_post["root_uid"] = item[2]
            a_post["mid"] = item[3]
            a_post["comment"] = item[4]
            a_post["retweeted"] = item[5]
            a_post["text"] = item[6]
            a_post["keywords_dict"] = item[7]
            a_post["timestamp"] = item[8]
            a_post["date"] = item[9].strftime('%Y-%m-%d')
            a_post["ip"] = item[10]
            a_post["geo"] = item[11]
            a_post["message_type"] = item[12]
            a_post["root_mid"] = item[13]
            a_post["source"] = item[14]
            a_post["store_timestamp"] = item[15]
            a_post["store_date"] = item[16].strftime('%Y-%m-%d')
            a_post["similar_event"] = item[17]
            hot_post_display.append(a_post)
        results = json.dumps(hot_post_display)
        return JsonResponse(results, safe=False)  # json [{data},{data}]



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
