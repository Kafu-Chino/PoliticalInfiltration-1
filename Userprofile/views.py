# -*- coding: utf-8 -*-
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
import time
import datetime
from collections import defaultdict
from django.db.models import Q
from Userprofile.models import *
from Mainevent.models import *
from Config.base import *
from Config.time_utils import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema
import json

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
        n_type = request.GET.get('n_type')
        date = request.GET.get('date')
        res_dict = defaultdict(dict)
        #origin_dict = {}
        #comment_dict={}

        t=datetime.datetime.strptime(date+ " 23:59:59", '%Y-%m-%d %H:%M:%S')
        #t = time.mktime(time.strptime(date, '%Y-%m-%d'))
        # 每日活动特征，从当前日期往前推7天展示 原创微博数、评论数、转发数、敏感微博数
        if n_type == "日":
            new_date = (t + datetime.timedelta(days=-7)).timestamp()
            result = UserBehavior.objects.filter(uid=uid, timestamp__gte=new_date,timestamp__lte=t.timestamp()).values(
                "store_date").annotate(originalnum_s=Sum("originalnum"), commentnum_s=Sum("commentnum"),
                                      retweetnum_s=Sum("retweetnum"), sensitivenum_s=Sum("sensitivenum"))
            if result.exists():
                for item in result:
                    td = item["store_date"]  #pop("timestamp") - 24 * 60 * 60
                    #res_dict[time.strftime("%Y-%m-%d", time.localtime(t))] = item
                    #res_dict[str(td)] = item
                    res_dict['originalnum'][str(td)] = item['originalnum_s']
                    res_dict['commentnum'][str(td)] = item['commentnum_s']
                    res_dict['retweetnum'][str(td)] = item['retweetnum_s']
                    res_dict['sensitivenum'][str(td)] = item['sensitivenum_s']
       
            else:
                return JsonResponse({"status":400, "error": "未找到该用户活动信息"},safe=False,json_dumps_params={'ensure_ascii':False}) 
        # 每周活动特征，从当前日期往前推5周展示 原创微博数、评论数、转发数、敏感微博数
        if n_type == "周":
            date_dict = {}
            for i in range(5):
                date_dict[i + 1] = (t + datetime.timedelta(weeks=(-1 * (i + 1)))).timestamp()
            date_dict[0] = t.timestamp()
            for i in range(5):
                result = UserBehavior.objects.filter(uid=uid, timestamp__gte=date_dict[i + 1],
                                                     timestamp__lt=date_dict[i]).aggregate(
                    originalnum_s=Sum("originalnum"), commentnum_s=Sum("commentnum"), retweetnum_s=Sum("retweetnum"),
                    sensitivenum_s=Sum("sensitivenum"))
                if list(result.values())[0]:
                    res_dict['originalnum'][time.strftime("%Y-%m-%d", time.localtime((date_dict[i])))] = result['originalnum_s']
                    res_dict['commentnum'][time.strftime("%Y-%m-%d", time.localtime((date_dict[i])))] = result['commentnum_s']
                    res_dict['retweetnum'][time.strftime("%Y-%m-%d", time.localtime((date_dict[i])))] = result['retweetnum_s']
                    res_dict['sensitivenum'][time.strftime("%Y-%m-%d", time.localtime((date_dict[i])))] = result['sensitivenum_s']
                    #res_dict[time.strftime("%Y-%m-%d", time.localtime((date_dict[i])))] = result
        # 每月活动特征，从当前日期往前推5月展示 原创微博数、评论数、转发数、敏感微博数
        if n_type == "月":
            date_dict = {}
            for i in range(5):
                date_dict[i + 1] = (t + datetime.timedelta(days=(-30 * (i + 1)))).timestamp()
            date_dict[0] = t.timestamp()
            for i in range(5):
                result = UserBehavior.objects.filter(uid=uid, timestamp__gte=date_dict[i + 1],
                                                     timestamp__lt=date_dict[i]).aggregate(
                    originalnum_s=Sum("originalnum"), commentnum_s=Sum("commentnum"), retweetnum_s=Sum("retweetnum"),
                    sensitivenum_s=Sum("sensitivenum"))
                if list(result.values())[0]:
                    res_dict['originalnum'][time.strftime("%Y-%m-%d", time.localtime((date_dict[i])))] = result['originalnum_s']
                    res_dict['commentnum'][time.strftime("%Y-%m-%d", time.localtime((date_dict[i])))] = result['commentnum_s']
                    res_dict['retweetnum'][time.strftime("%Y-%m-%d", time.localtime((date_dict[i])))] = result['retweetnum_s']
                    res_dict['sensitivenum'][time.strftime("%Y-%m-%d", time.localtime((date_dict[i])))] = result['sensitivenum_s']
        return JsonResponse(res_dict)
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
        n_type = request.GET.get('n_type') if request.GET.get('n_type') else 3
        date = request.GET.get('date')
        t=datetime.datetime.strptime(date+ " 23:59:59", '%Y-%m-%d %H:%M:%S')
        res_dict = {}
        cal_date = (t + datetime.timedelta(days=-30)).timestamp()
        if n_type == 1:
            cal_date = (t + datetime.timedelta(days=-1)).timestamp()
        elif n_type == 2:
            cal_date = (t + datetime.timedelta(days=-7)).timestamp()
        elif n_type == 3:
            cal_date = (t + datetime.timedelta(days=-30)).timestamp()
        elif n_type == 4:
            cal_date = (t + datetime.timedelta(days=-90)).timestamp()

        day_result = UserActivity.objects.filter(uid=uid, timestamp__gte=cal_date,timestamp__lte=t.timestamp()).values("geo", "send_ip").annotate(
            statusnum_s=Sum("statusnum"), sensitivenum_s=Sum("sensitivenum")).order_by("-sensitivenum_s")
        res_dict["day_result"] = list(day_result)
        # 热度展示
        
        geo_map_result = UserActivity.objects.filter(uid=uid, timestamp__gte=cal_date).values("geo").annotate(
            statusnum_s=Sum("statusnum")).order_by("-statusnum_s")
        print(geo_map_result)
        res_dict["geo_map_result"] = list(geo_map_result)
        


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
        #re2 = defaultdict(list)
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
            re = dict(sorted(new_topic.items(),key=lambda x:x[1],reverse=True)[:5])
            #print(type(re))
            #re = json.dumps(re,ensure_ascii=False)
            #re = json.load(re,ensure_ascii=False)
            return JsonResponse(re,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "未找到该用户信息"},safe=False,json_dumps_params={'ensure_ascii':False}) 




class Show_keyword(APIView):
    """展示用户关键词、参与话题、敏感词
       输入uid
       输出{‘uid’:{‘keywords’:{…},’sensitive_words’:{},’hastags’:{}}"""
    def get(self,request):
        re1 = {}
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
                re1["keywords"] = dict(sorted(kw.items(),key=lambda x:x[1],reverse=True)[:5])
                re1["sensitive_words"] = sw
                re1["hastags"] = dict(sorted(ht.items(),key=lambda x:x[1],reverse=True)[:5])
            return JsonResponse(re1,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "未找到该用户信息"},safe=False,json_dumps_params={'ensure_ascii':False})

class Show_contact(APIView):
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
        #h_id = request.GET.get("wb_id")  # 若该条人工输入事件从微博而来 则需输入来源微博的id
        #result = Task.objects.filter(~Q(mid=''), mid=h_id) #判断从微博得来的事件是否已存在，若微博ID未给出返回一个空值
        result = Figure.objects.filter(f_id=uid)
        if result.exists():
            return JsonResponse({"status":400, "error": "人物已存在"},safe=False,json_dumps_params={'ensure_ascii':False})
        if f_id and nick :
            Figure.objects.create(f_id=f_id, uid=uid, nick_name=nick,user_location=location,fansnum=fans,
                                friendsnum=friends,political = political,domain=domain)
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
        result = Figure.objects.all()[int(limit)*(int(page_id)-1):int(limit)*int(page_id)]
        res_list = []
        if result.exists():
            for item in result:
                event_count = 0
                info_count = 0
                #sdate = item.begin_date.strftime('%Y-%m-%d %H:%M:%S')
                #edate = item.end_date.strftime('%Y-%m-%d %H:%M:%S')
                fid = item.f_id
                event_count = Figure.objects.get(f_id=fid).event.all().count()
                info_count = Information.objects.filter(uid=fid).count()
                res_list.append({"f_id":fid,"nick_name":item.nick_name,"fansnum":item.fansnum,'friendsnum':item.friendsnum,'create_at':item.create_at,'event_count':event_count,'info_count':info_count,'user_location':item.user_location})
            '''
            page = Paginator(res_list, limit)
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
            #re = json.dumps(list(results),ensure_ascii=False)
            #re = json.loads(re)
            return JsonResponse(res_list,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "无人物"},safe=False)


class show_figure_info(APIView):
    """展示人物详细信息"""
    def get(self,request):
        """获取uid 返回返回字段f_id为用户账号，nick_name为昵称,event_count为参与事件数，info_count为敏感信息数
          fansnum粉丝数,friendsnum关注数,political政治倾向,domain领域,user_location地点"""
        event_count = 0
        info_count = 0
        res_dict = {}
        fid = request.GET.get("uid")
        res = Figure.objects.filter(f_id=fid).values("f_id","nick_name","fansnum",'friendsnum','political','domain','user_location','create_at')
        if res.exists():
            res_event = Figure.objects.get(f_id=fid).event.all()
            event_count = Figure.objects.get(f_id=fid).event.all().count()
            info_count = Information.objects.filter(uid=fid).count()
            res_dict["uid"] = fid
            for re in res:
                res_dict["nick_name"]=re["nick_name"]
                res_dict["fansnum"]=re["fansnum"]
                res_dict['friendsnum']=re['friendsnum']
                #print(re["create_at"])
                res_dict['create_at']=re['create_at']
                res_dict['user_location']=re['user_location']
                res_dict["domain"]=re["domain"]
                res_dict["political"]=re["political"]
            res_dict['event_count']=event_count
            res_dict['info_count']=info_count
            return JsonResponse(res_dict,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "无人物"},safe=False)



class Association(APIView):
    """用户关联分析接口"""

    def get(self, request):
        """
        获取uid，返回用户关联分析详情，包括用户参与的相关事件、相关信息详情,
        数据格式{
                    "event":[{"event_name": event_name1, "keywords": keywords_dict1},{}],
                    "information":[{"text": text1, "hazard_index": hazard_index1, "mid": i.mid},{}]
                }
        """
        res_dict = defaultdict(list)
        uid = request.GET.get('uid')
        res_event = Figure.objects.filter(f_id=uid).first().event_set.all()
        for e in res_event:
            res_dict["event"].append({"event_name": e.event_name, "keywords": e.keywords_dict})
        res_information = Information.objects.filter(uid=uid)
        for i in res_information:
            res_dict["information"].append({"text": i.text, "hazard_index": i.hazard_index, "mid": i.mid})
        return JsonResponse(res_dict)


class related_info(APIView):
    """人物-信息关联分析"""
    def get(self,request):
        res_dict = []
        fid = request.GET.get('uid')
        limit = request.GET.get("limit")
        page_id = request.GET.get('page_id')
        res = Information.objects.filter(uid=fid)
        if res.exists():
            for i in res:
                lt = time.localtime(i.timestamp)
                itime = time.strftime('%Y-%m-%d %H:%M:%S',lt)
                #print(itime)
                res_dict.append({'text': i.text,'time':itime,'geo':i.geo})
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



class related_event(APIView):
    """人物-事件相关信息"""
    def get(self,request):
        res_dict = []
        fid = request.GET.get('uid')
        limit = request.GET.get("limit")
        page_id = request.GET.get('page_id')
        res = Figure.objects.filter(uid=fid)
        if res.exists():
            res_event = Figure.objects.get(f_id=fid).event.all()
            for e in res_event:
                #lt = time.localtime(i.timestamp)
                #itime = time.strftime('%Y-%m-%d %H:%M:%S',lt)
                #print(itime)
                sdate = e.begin_date.strftime('%Y-%m-%d %H:%M:%S')
                edate = e.end_date.strftime('%Y-%m-%d %H:%M:%S')
                res_dict.append({'event_name': e.event_name,'keywords':e.keywords_dict,'begin_date':sdate,'end_date':edate})
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




class search_figure(APIView):
    """展示所搜寻人物信息"""
    def get(self, request):
        """展示人物,该文档返回Figure表中存在的需要展示的数据，返回字段f_id为用户账号，nick_name为昵称
          fansnum粉丝数,friendsnum关注数,political政治倾向,domain领域,user_location地点"""
        info = request.GET.get("info")
        #results={}
        limit = request.GET.get("limit")
        page_id = request.GET.get('page_id')
        if page_id is None:
            page_id = 1
        if limit is None:
            limit = 10
        result = Figure.objects.filter(Q(nick_name__contains = info) | Q(uid__contains = info)).values("f_id","nick_name","fansnum",'friendsnum','political','domain','user_location')[int(limit)*(int(page_id)-1):int(limit)*int(page_id)]
        if result.exists():
            #results["result"] = list(result)
            #print(type(results))
            #json_data = serializers.serialize("json",results)
            #re = json.loads(json_data)
            #print(results)
            re = json.dumps(list(result),ensure_ascii=False)
            #re = re.replace("\\","")
            #re = re.Replace("[","")
            re = json.loads(re)
            return JsonResponse(re,safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "该人物不存在"},safe=False,json_dumps_params={'ensure_ascii':False})





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
        res_dict = {}
        # 每日情绪特征，从当前日期往前推7天展示 积极微博数，中性微博数，消极微博数
        if n_type == "日":
            new_date = (datetime.datetime.now() + datetime.timedelta(days=-7)).timestamp()
            result = UserSentiment.objects.filter(uid=uid, timestamp__gte=new_date).values(
                "timestamp").annotate(positive_s=Sum("positive"), nuetral_s=Sum("nuetral"),
                                      negtive_s=Sum("negtive"))
            for item in result:
                t = item.pop("timestamp") - 24 * 60 * 60
                res_dict[time.strftime("%Y-%m-%d", time.localtime(t))] = item
        # 每周情绪特征，从当前日期往前推5周展示 积极微博数，中性微博数，消极微博数
        if n_type == "周":
            date_dict = {}
            for i in range(5):
                date_dict[i + 1] = (datetime.datetime.now() + datetime.timedelta(weeks=(-1 * (i + 1)))).timestamp()
            date_dict[0] = time.time()
            for i in range(5):
                result = UserSentiment.objects.filter(uid=uid, timestamp__gte=date_dict[i + 1],
                                                     timestamp__lt=date_dict[i]).aggregate(positive_s=Sum("positive"), nuetral_s=Sum("nuetral"),
                                      negtive_s=Sum("negtive"))
                if list(result.values())[0] or list(result.values())[1] or list(result.values())[2]:
                    res_dict[time.strftime("%Y-%m-%d", time.localtime((date_dict[i]) - 24 * 60 * 60))] = result
        # 每月情绪特征，从当前日期往前推5月展示 积极微博数，中性微博数，消极微博数
        if n_type == "月":
            date_dict = {}
            for i in range(5):
                date_dict[i + 1] = (datetime.datetime.now() + datetime.timedelta(days=(-30 * (i + 1)))).timestamp()
            date_dict[0] = time.time()
            for i in range(5):
                result = UserSentiment.objects.filter(uid=uid, timestamp__gte=date_dict[i + 1],
                                                     timestamp__lt=date_dict[i]).aggregate(positive_s=Sum("positive"), nuetral_s=Sum("nuetral"),
                                      negtive_s=Sum("negtive"))
                if list(result.values())[0] or list(result.values())[1] or list(result.values())[2]:
                    res_dict[time.strftime("%Y-%m-%d", time.localtime((date_dict[i]) - 24 * 60 * 60))] = result
        return JsonResponse(res_dict)

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
        print (uid)
        print (NewUserInfluence.objects.filter(uid=uid).exists())
        res_dict = {}
        # 每日影响力特征，从当前日期往前推7天展示 影响力 活跃度 重要度 敏感度
        if n_type == "日":
            new_date = (datetime.datetime.now() + datetime.timedelta(days=-7)).timestamp()
            result = NewUserInfluence.objects.filter(uid=uid, timestamp__gte=new_date).values(
                "timestamp","influence","importance","sensitity","activity")
            for item in result:
                t = item.pop("timestamp") - 24 * 60 * 60
                res_dict[time.strftime("%Y-%m-%d", time.localtime(t))] = item
        # 每周影响力特征，从当前日期往前推5周展示
        if n_type == "周":
            date_dict = {}
            for i in range(5):
                date_dict[i + 1] = (datetime.datetime.now() + datetime.timedelta(weeks=(-1 * (i + 1)))).timestamp()
            date_dict[0] = time.time()
            for i in range(5):
                print (date_dict[i + 1],date_dict[i])
                result =NewUserInfluence.objects.filter(uid=uid, timestamp__gte=date_dict[i + 1],
                                                      timestamp__lt=date_dict[i]).aggregate(
                    influence=Avg("influence"), importance=Avg("importance"),
                    sensitity=Avg("sensitity"),activity=Avg("activity"))
                if list(result.values())[0] or list(result.values())[1] or list(result.values())[2]:
                    res_dict[time.strftime("%Y-%m-%d", time.localtime((date_dict[i]) - 24 * 60 * 60))] = result
        # 每月情绪特征，从当前日期往前推5月展示
        if n_type == "月":
            date_dict = {}
            for i in range(5):
                date_dict[i + 1] = (datetime.datetime.now() + datetime.timedelta(days=(-30 * (i + 1)))).timestamp()
            date_dict[0] = time.time()
            for i in range(5):
                result = NewUserInfluence.objects.filter(uid=uid, timestamp__gte=date_dict[i + 1],
                                                      timestamp__lt=date_dict[i]).aggregate(
                    influence=Avg("influence"), importance=Avg("importance"),
                    sensitity=Avg("sensitity"),activity=Avg("activity"))
                if list(result.values())[0] or list(result.values())[1] or list(result.values())[2]:
                    res_dict[time.strftime("%Y-%m-%d", time.localtime((date_dict[i]) - 24 * 60 * 60))] = result
        return JsonResponse(res_dict)