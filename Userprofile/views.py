# -*- coding: utf-8 -*-

from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.db.models import Q, Sum
import json
import time, datetime
from collections import defaultdict

from Mainevent.models import *

from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema


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


class BasicInfo(APIView):
    """用户基本信息接口"""

    def get(self, request):
        """获取uid，返回用户详情"""
        f_id = request.GET.get('uid')
        # result = Figure.objects.filter(f_id="1041560960").first()
        result = Figure.objects.filter(f_id=f_id).first()
        res_dict = {}
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
        # print(res_dict)
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
        # uid = "1041560960"
        # n_type = "日"
        # n_type = "周"
        # n_type = "月"
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
        # print(res_dict)
        return JsonResponse(res_dict)


class User_Activity(APIView):
    """用户地域特征接口"""

    def get(self, request):
        """
        获取uid，返回用户地域特征详情，包括根据地理位置、IP地址每日、每周活跃程度排序，
        数据格式{
                    "geo_day_result":[{"geo1":geo_name,"statusnum":30},{}],
                    "geo_week_result":[{"geo1":geo_name,"statusnum":30},{}],
                    "ip_day_result":[{"ip1":send_ip,"statusnum":30},{}],
                    "ip_week_result":[{"ip1":send_ip,"statusnum":30},{}],
                    "route_list":[{"s":geo,"e":geo},{}]
                }
        """
        uid = request.GET.get('uid')
        # uid = "1563323381"
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
        # uid = "1563323381"
        res_event = Figure.objects.filter(f_id=uid).first().event_set.all()
        for e in res_event:
            res_dict["event"].append({"event_name": e.event_name, "keywords": e.keywords_dict})
        res_information = Information.objects.filter(uid=uid)
        for i in res_information:
            res_dict["information"].append({"text": i.text, "hazard_index": i.hazard_index})
        # print(res_dict)
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
