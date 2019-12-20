from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.db.models import Q, Sum
import json
import numpy as np
import time, datetime
from collections import defaultdict
from django.db.models.aggregates import Count
from Userprofile.models import *
from Mainevent.models import *

from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema


class Test(APIView):
    """测试页面"""

    def get(self, request):
        """GET方法的功能说明写在这里"""
        return HttpResponse('欢迎来到Userprofile测试页面！')

    # def post(self, request):
    #     """POST方法的功能说明写在这里"""
    #     return HttpResponse('这是测试的POST方法')

    # def put(self, request):
    #     """PUT方法的功能说明写在这里"""
    #     return HttpResponse('这是测试的PUT方法')

    # def delete(self, request):
    #     """DELETE方法的功能说明写在这里"""
    #     return HttpResponse('这是测试的DELETE方法')


class BasicInfo(APIView):
    """用户基本信息接口"""

    def get(self, request):
        """获取uid，返回用户详情"""
        res_dict = {}
        f_id = request.GET.get('uid')
        result = Figure.objects.filter(f_id=f_id).first()
        res_dict["uid"] = result.uid
        res_dict["nick_name"] = result.nick_name
        res_dict["age"] = datetime.date.today().year - result.user_birth.year
        # now = datetime.date.today()
        # birth = result.user_birth
        # if now.month < birth.month:  # 如果月份比今天大，没过生日，则年份相减再减一
        #     res_dict["age"] = now.year - birth.year - 1
        # if now.month > birth.month:  # 如果月份比今天小，过生日了，则年份相减
        #     res_dict["age"] = now.year - birth.year
        # if now.month == birth.month and now.day < birth.day:  # 如果月份相等，生日比今天大，没过生日
        #     res_dict["age"] = now.year - birth.year - 1
        # if now.month == birth.month and now.day > birth.day:  # 如果月份相等，生日比今天小，过生日了
        #     res_dict["age"] = now.year - birth.year
        res_dict["statusnum"] = result.statusnum
        res_dict["political"] = result.political if result.political else "无"
        res_dict["domain"] = result.domain if result.domain else "无"
        res_dict["create_at"] = time.strftime("%Y-%m-%d", time.localtime(result.create_at))
        res_dict["sex"] = ("男" if result.sex == 1 else "女") if result.sex else "无"
        res_dict["friendsnum"] = result.friendsnum
        res_dict["fansnum"] = result.fansnum
        res_dict["user_location"] = result.user_location if result.user_location else "无"
        res_dict["description"] = result.description if len(result.description) != 0 else "无"
        return JsonResponse(res_dict)

    def post(self, request):
        """"""
        return HttpResponse('这是POST方法')


class User_Behavior(APIView):
    """用户活动特征接口"""

    def get(self, request):
        """
        获取uid，返回用户活动特征详情，根据传入参数n_type 日 周 月 返回相应数据结果，
        数据格式{date1:{originalnum:10,commentnum:20,retweetnum:30},date2:{originalnum: 10,commentnum:20,retweetnum:30}}
        """
        uid = request.GET.get('uid')
        n_type = request.GET.get('n_type')
        res_dict = {}
        # 每日活动特征，从当前日期往前推7天展示 原创微博数、评论数、转发数
        if n_type == "日":
            new_date = (datetime.datetime.now() + datetime.timedelta(days=-7)).timestamp()
            result = UserBehavior.objects.filter(uid=uid, timestamp__gte=new_date).values(
                "timestamp").annotate(originalnum_s=Sum("originalnum"), commentnum_s=Sum("commentnum"),
                                      retweetnum_s=Sum("retweetnum"))
            for item in result:
                t = item.pop("timestamp") - 24 * 60 * 60
                res_dict[time.strftime("%Y-%m-%d", time.localtime(t))] = item
        # 每周活动特征，从当前日期往前推5周展示 原创微博数、评论数、转发数
        if n_type == "周":
            date_dict = {}
            for i in range(5):
                date_dict[i + 1] = (datetime.datetime.now() + datetime.timedelta(weeks=(-1 * (i + 1)))).timestamp()
            date_dict[0] = time.time()
            for i in range(5):
                result = UserBehavior.objects.filter(uid=uid, timestamp__gte=date_dict[i + 1],
                                                     timestamp__lt=date_dict[i]).aggregate(
                    originalnum_s=Sum("originalnum"), commentnum_s=Sum("commentnum"), retweetnum_s=Sum("retweetnum"))
                if list(result.values())[0]:
                    res_dict[time.strftime("%Y-%m-%d", time.localtime((date_dict[i]) - 24 * 60 * 60))] = result
        # 每月活动特征，从当前日期往前推5月展示 原创微博数、评论数、转发数
        if n_type == "月":
            date_dict = {}
            for i in range(5):
                date_dict[i + 1] = (datetime.datetime.now() + datetime.timedelta(days=(-30 * (i + 1)))).timestamp()
            date_dict[0] = time.time()
            for i in range(5):
                result = UserBehavior.objects.filter(uid=uid, timestamp__gte=date_dict[i + 1],
                                                     timestamp__lt=date_dict[i]).aggregate(
                    originalnum_s=Sum("originalnum"), commentnum_s=Sum("commentnum"), retweetnum_s=Sum("retweetnum"))
                if list(result.values())[0]:
                    res_dict[time.strftime("%Y-%m-%d", time.localtime((date_dict[i]) - 24 * 60 * 60))] = result
        return JsonResponse(res_dict)


class User_Activity(APIView):
    """用户地域特征接口"""

    def get(self, request):
        """
        获取uid，返回用户地域特征详情，包括根据地理位置、IP地址每日、每周活跃程度降序排序，
        数据格式{
                    "geo_day_result":[{"geo1":geo_name,"statusnum":30},{}],
                    "geo_week_result":[{"geo1":geo_name,"statusnum":30},{}],
                    "ip_day_result":[{"ip1":send_ip,"statusnum":30},{}],
                    "ip_week_result":[{"ip1":send_ip,"statusnum":30},{}],
                    "route_list":[{"s":geo,"e":geo},{}]
                }
        """
        uid = request.GET.get('uid')
        res_dict = {}
        week_date = (datetime.datetime.now() + datetime.timedelta(days=-7)).timestamp()
        day_date = (datetime.datetime.now() + datetime.timedelta(days=-1)).timestamp()
        geo_day_result = UserActivity.objects.filter(uid=uid, timestamp__gte=day_date).values("geo").annotate(
            statusnum_s=Sum("statusnum")).order_by("-statusnum_s")
        res_dict["geo_day_result"] = list(geo_day_result)
        geo_week_result = UserActivity.objects.filter(uid=uid, timestamp__gte=week_date).values(
            "geo").annotate(statusnum_s=Sum("statusnum")).order_by("-statusnum_s")
        res_dict["geo_week_result"] = list(geo_week_result)
        ip_day_result = UserActivity.objects.filter(uid=uid, timestamp__gte=day_date).values(
            "send_ip").annotate(statusnum_s=Sum("statusnum")).order_by("-statusnum_s")
        res_dict["ip_day_result"] = list(ip_day_result)
        ip_week_result = UserActivity.objects.filter(uid=uid, timestamp__gte=week_date).values(
            "send_ip").annotate(statusnum_s=Sum("statusnum")).order_by("-statusnum_s")
        res_dict["ip_week_result"] = list(ip_week_result)
        geo_dict = UserActivity.objects.filter(uid=uid, timestamp__gte=week_date).values("timestamp", "geo").annotate(
            statusnum_s=Sum("statusnum"))
        route_dict = defaultdict(dict)
        for item in geo_dict:
            t = item.pop("timestamp")
            route_dict[t][item["geo"]] = item["statusnum_s"]
        geo_dict_item = list(route_dict.items())
        route_list = []
        geo_dict_item = sorted(geo_dict_item, key=lambda x: x[0])
        geo_index = 0
        for i in range(len(geo_dict_item)):
            if not geo_dict_item[i][1]:
                continue
            item = {'s': max(geo_dict_item[i][1], key=geo_dict_item[i][1].get).split('&')[1], 'e': ''}
            route_list.append(item)
            if geo_index > 0:
                route_list[geo_index - 1]['e'] = max(geo_dict_item[i][1], key=geo_dict_item[i][1].get).split('&')[1]
            geo_index += 1
        if len(route_list) > 1:
            del (route_list[-1])
        elif len(route_list) == 1:
            route_list[0]['e'] = route_list[0]['s']
        for item in route_list:
            if not (item['s'] and item['e']):
                route_list.remove(item)
        res_dict["route_list"] = route_list
        return JsonResponse(res_dict)


class Association(APIView):
    """用户关联分析接口"""

    def get(self, request):
        """获取uid，返回用户关联分析详情，包括用户参与的相关事件、相关信息详情,
        数据格式{
                    "event":[{"event_name": event_name1, "keywords": keywords_dict1},{}],
                    "information":[{"text": text1, "hazard_index": hazard_index1},{}]
                }
        """
        res_dict = defaultdict(list)
        uid = request.GET.get('uid')
        res_event = Figure.objects.filter(f_id=uid).first().event_set.all()
        for e in res_event:
            res_dict["event"].append({"event_name": e.event_name, "keywords": e.keywords_dict})
        res_information = Information.objects.filter(uid=uid)
        for i in res_information:
            res_dict["information"].append({"text": i.text, "hazard_index": i.hazard_index})
        return JsonResponse(res_dict)


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
    def get(self,request):
        re = []
        uid = request.GET.get("uid")
        start_time = request.GET.get("time1")
        end_time = request.GET.get("time2")
        result = UserTopic.objects.filter(uid = uid)  #, store_date__range=(start_time,end_time)
        #return HttpResponse(typeof(result))
        if result.exists():
            json_data = serializers.serialize("json",result)
            results = json.loads(json_data)
            #return JsonResponse(results,safe=False)
            #'''
            count = np.zeros(19)
            for i in results:
                #return JsonResponse(i,safe=False)
                i["fields"]["topics"]["art"] += count[0]
                count[0] = i["fields"]["topics"]["art"]
                i["fields"]["topics"]["computer"]+= count[1]
                count[1] = i["fields"]["topics"]["computer"]
                i["fields"]["topics"]["economic"] += count[2]
                count[2] = i["fields"]["topics"]["economic"]
                i["fields"]["topics"]["education"] += count[3]
                count[3] = i["fields"]["topics"]["education"]
                i["fields"]["topics"]["environment"] += count[4]
                count[4] = i["fields"]["topics"]["environment"]
                i["fields"]["topics"]["medicine"] += count[5]
                count[5] = i["fields"]["topics"]["medicine"]
                i["fields"]["topics"]["military"] += count[6]
                count[6] = i["fields"]["topics"]["military"]
                i["fields"]["topics"]["politics"] += count[7]
                count[7] = i["fields"]["topics"]["politics"]
                i["fields"]["topics"]["sports"] += count[8]
                count[8] = i["fields"]["topics"]["sports"]
                i["fields"]["topics"]["traffic"] += count[9]
                count[9] = i["fields"]["topics"]["traffic"]
                i["fields"]["topics"]["life"] += count[10]
                count[10] = i["fields"]["topics"]["life"]
                i["fields"]["topics"]["anti-corruption"] += count[11]
                count[11] = i["fields"]["topics"]["anti-corruption"]
                i["fields"]["topics"]["employment"] += count[12]
                count[12] = i["fields"]["topics"]["employment"]
                i["fields"]["topics"]["fear-of-violence"] += count[13]
                count[13] = i["fields"]["topics"]["fear-of-violence"]
                i["fields"]["topics"]["house"] += count[14]
                count[14] = i["fields"]["topics"]["house"]
                i["fields"]["topics"]["law"] += count[15]
                count[15] = i["fields"]["topics"]["law"]
                i["fields"]["topics"]["peace"] += count[16]
                count[16] = i["fields"]["topics"]["peace"]
                i["fields"]["topics"]["religion"] += count[17]
                count[17] = i["fields"]["topics"]["religion"]
                i["fields"]["topics"]["social-security"] += count[18]
                count[18] = i["fields"]["topics"]["social-security"]
                re.append(i["fields"]["topics"])
            re = sorted(re[len(results)-1].items(),key=lambda x:x[1],reverse=True)[:5]
            #result = sorted(result[0], reverse = True)
            #return HttpResponse(re)
            
            return JsonResponse(re,safe=False)
        else:
            return JsonResponse({"status":400, "error": "未找到该用户信息"},safe=False,json_dumps_params={'ensure_ascii':False}) 

class Show_contact(APIView):
    def get(self,request):
        user_source=defaultdict(list)
        #user_target=defaultdict(list)
        uid = request.GET.get("uid")
        start_time = request.GET.get("time1")
        end_time = request.GET.get("time2")
        result1 = UserSocialContact.objects.filter(target = uid, store_date__range=(start_time,end_time))\
                   .values('source').annotate(c=Count('uid')).filter(c__gte=5)
        result2 = UserSocialContact.objects.filter(source = uid, store_date__range=(start_time,end_time))\
                   .values('target').annotate(c=Count('uid')).filter(c__gte=5)
        if result1.exists():
            for re in result1:
                test = Figure.objects.filter(uid=re['source'])
                if test.exists():
                    user_source["in"].append({'uid':re['uid'],'insource':re['source']})
                else:
                    user_source["out"].append({'uid':re['uid'],'outsource':re['source']})
            #json_source = serializers.serialize("json",in_)
            #results1 = json.loads(json_source)
            return JsonResponse(user_source,safe=False)
        if result2.exists():
            json_target = serializers.serialize("json",result2)
            results2 = json.loads(json_target)
            return JsonResponse(results2,safe=False)
        else:
            return JsonResponse({"status":400, "error": "未找到符合条件的用户"},safe=False,json_dumps_params={'ensure_ascii':False})
