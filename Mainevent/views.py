# -*- coding: utf-8 -*-
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.db.models import Q
from Mainevent.models import Task
import json
import time,datetime


from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema

class Test(APIView):
    """测试页面"""
    def get(self, request):
        """获取用户信息"""
        # do something
        return HttpResponse('Hello world')

    def post(self, request):
        """获取用户信息"""
        pass

    def put(self, request):
        """更新用户信息"""
        pass

    def delete(self, request):
        """删除用户信息"""
        pass


class AddByInput(APIView):
    """手动添加事件入库"""
# task_type 0->新事件入库 1->作为相关事件入库
# into_type 0->人工手动添加 1->从热贴推送入库 2->系统计算入库
# status 0->未计算 1->已计算 2->计算中 3->计算失败
    def post(self,request):
        """获取添加信息，输入name,keywords,content,wb_id调取事件名称/关键词和内容，输出状态及提示：400 状态错误，201写入成功"""
        times = int(time.time())
        dates = datetime.datetime.now().strftime('%Y-%m-%d')  # 获取当前时间戳和日期
        event = request.POST
        event_id = event["name"] + str(times)  # 事件名+时间戳作为任务ID
        event_content = event["content"]  # 获取事件内容
        keywords = event["keywords"]  # 获取事件关键词
        h_id = event["wb_id"]  #获取微博ID 可为空
        result = Task.objects.filter(~Q(mid=''), mid=h_id)  # 判断从微博得来的事件是否已存在，若微博ID未给出返回一个空值
        if event_id and keywords and event_content:
            if result.exists():
                return JsonResponse({"status": 400, "error": "事件已存在"},safe=False,json_dumps_params={'ensure_ascii':False},charset='utf-8')
            else:
                Task.objects.create(t_id=event_id, task_type="0", into_type="0", status=0, text=event_content,
                                    keywords_dict=keywords, mid=h_id, into_timestamp=times,
                                    into_date=dates)
                return JsonResponse({"status": 201, "msg": "新事件入库成功"},safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status": 400, "error": "请输入事件的名称,关键词和内容"},safe=False,json_dumps_params={'ensure_ascii':False})

    def get(self,request):
        """获取添加信息，输入name,keywords,content,wb_id调取事件名称/关键词和内容，输出状态及提示：400 状态错误，201写入成功"""
        times = int(time.time())
        dates = datetime.datetime.now().strftime('%Y-%m-%d')  # 获取当前时间戳和日期
        event_id = str(request.GET.get("name")) + str(times)  # 事件名+时间戳作为任务ID
        event_content = request.GET.get("content")
        keywords = request.GET.get("keywords")
        h_id = request.GET.get("wb_id")  # 若该条人工输入事件从微博而来 则需输入来源微博的id
        result = Task.objects.filter(~Q(mid=''), mid=h_id) #判断从微博得来的事件是否已存在，若微博ID未给出返回一个空值
        if event_id and keywords and event_content:
            if result.exists():
                return JsonResponse({"status":400, "error": "事件已存在"},safe=False, json_dumps_params={'ensure_ascii':False})
            else:
                Task.objects.create(t_id=event_id, task_type="0", into_type="0", status=0, text=event_content,keywords_dict=keywords, mid=h_id,into_timestamp=times,
                                    into_date=dates)
            return JsonResponse({"status":201, "msg": "新事件入库成功"},safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({"status":400, "error": "请输入事件的名称，关键词和内容"},safe=False,json_dumps_params={'ensure_ascii':False})


class AddFromPush(APIView):
    """业务员选择推出热贴入库，输入mid(微博id)，rmid(相关事件id），keywords_dict(关键词），输出状态码和提示：400 状态错误，201写入成功"""
    def get(self, request):
        """获取推送热贴相关心信息入库"""
        event_id = request.GET.get('mid')  # 从推送得到微博ID
        relative_id = request.GET.get("rmid")  # 若作为相关事件入库，获取相关事件的ID，目前设定只有一个相关事件
#        relative_id = ','.join(relative_ids)
        times = time.time()
        keywords = request.GET.get("keywords_dict")
        dates = datetime.datetime.now().strftime('%Y-%m-%d')
        result = Task.objects.filter(mid=event_id)
        if result.exists():
            return JsonResponse({"status":400, "error": "事件已存在"},safe=False,json_dumps_params={'ensure_ascii':False})
        elif relative_id == "":  # 判断是否选中了相关事件,若未选中，其rmid为空
            Task.objects.create(t_id=event_id, task_type="0", into_type="1", status="0", keywords_dict=keywords, into_timestamp=times, into_date=dates)
            return JsonResponse({"status": 201, "msg": "新事件入库成功"},safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            Task.objects.create(t_id=event_id, task_type="1", into_type="1", e_id=relative_id, status="0", keywords_dict=keywords, into_timestamp=times, into_date=dates)
            return JsonResponse({"status": 201, "msg": "相关事件入库成功"},safe=False,json_dumps_params={'ensure_ascii':False})


class AddBySystem(APIView):
    """系统算法判断是否添加入库"""
    pass


class Show(APIView):
    """展示任务列表"""
    def get(self, request):
        result = Task.objects.filter()
        json_data = serializers.serialize("json",result)
        results = json.loads(json_data)
        return JsonResponse(results,safe=False)
