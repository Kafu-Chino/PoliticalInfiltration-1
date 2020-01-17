# -*- coding: utf-8 -*-

from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
import time
import datetime
from Informationspread.models import *

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


class Show_Info(APIView):
    """展示信息传播态势接口"""

    def get(self, request):
        """
        获取微博mid，返回微博传播态势详情，可指定返回日期长度，默认为7天;
        返回格式: {date1:{spread_count_s:10},
                    date2:{spread_count_s: 10},
                    ...}
        """
        res_dict = {}
        mid = request.GET.get('mid')
        n = request.GET.get('n') if request.GET.get('n') else 7
        new_date = (datetime.datetime.now() + datetime.timedelta(days=-n)).timestamp()
        result = Informationspread.objects.filter(mid=mid, timestamp__gte=new_date).values(
            "timestamp").annotate(spread_count_s=Sum("spread_count"))
        for item in result:
            t = item.pop("timestamp") - 24 * 60 * 60
            res_dict[time.strftime("%Y-%m-%d", time.localtime(t))] = item
        return JsonResponse(res_dict)

    def post(self, request):
        """"""
        return HttpResponse('这是POST方法')
