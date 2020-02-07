from django.shortcuts import render

# Create your views here.
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.core import serializers
from .models import *
import time

from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema
from .敏感词扩展.sensitive_word_extent import extent


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


class Show_sensitive_word(APIView):
    """展示通用敏感词"""
    def get(self, request):
        """展示通用敏感词列表,该文档返回SensitiveWord表中存在的需要展示的数据，其中返回的字段prototype为通用敏感词原型"""
        result = SensitiveWord.objects.filter(transform=None, perspective_bias=0).values('prototype')
        if result.exists():
            return HttpResponse(result)
        else:
            return JsonResponse({"status":400, "error": "无通用敏感词"},safe=False)
        json_data = serializers.serialize("json", result)
        results = json.loads(json_data)
        return JsonResponse(results, safe=False)


class Show_sensitive_word_transform(APIView):
    """展示通用敏感词变型，点击敏感词传入prototype"""
    def get(self, request):
        prototype = request.GET.get("prototype")
        result = SensitiveWord.objects.filter(prototype=prototype).values('transform')
        if result.exists():
            return HttpResponse(result)
        else:
            return JsonResponse({"status":400, "error": "无敏感词变型"},safe=False)
        json_data = serializers.serialize("json", result)
        results = json.loads(json_data)
        return JsonResponse(results, safe=False)


class Add_sensitive_word(APIView):
    """添加敏感词入库，并自动将其变型加入库中"""
    def get(self,request):
        """人工添加敏感词：输入敏感词原型prototype;输出状态及提示：400 状态错误，201写入成功"""
        prototype = request.GET.get("prototype")
        #判断敏感词是否存在
        if prototype:
            result = SensitiveWord.objects.filter(prototype=prototype)
            if not result.exists():
                times = int(time.time())
                SensitiveWord.objects.create(s_id=str(times) + prototype, prototypy=prototype, perspective_bias=0)
                transforms = extent(prototype)
                for transform in transforms:
                    SensitiveWord.objects.create(s_id=str(times)+transform, prototypy=prototype, transform=transform, perspective_bias=0)
                return JsonResponse({"status":201, "msg": "任务成功添加"},safe=False,json_dumps_params={'ensure_ascii':False})
            else:
                return JsonResponse({"status": 400, "error": "敏感词已存在"}, safe=False,json_dumps_params={'ensure_ascii': False})

        else:
            return JsonResponse({"status":400, "error": "请输入敏感词"},safe=False,json_dumps_params={'ensure_ascii':False})


class Delete_sensitive_word_transform(APIView):
    """删除敏感词变型，点击叉号删除该变型，传入变型transform"""
    def get(self,request):
        """人工删除敏感词：输入敏感词变型transform;输出状态及提示：400 状态错误，201删除成功"""
        transform = request.GET.get("transform")
        result = SensitiveWord.objects.filter(transform=transform)
        if result.exists():
            try:
                SensitiveWord.objects.filter(transform=transform).delete()
                return JsonResponse({"status":201, "msg": "敏感词已删除"},safe=False,json_dumps_params={'ensure_ascii':False})
            except:
                return JsonResponse({"status":400, "error": "删除失败"},safe=False,json_dumps_params={'ensure_ascii':False})

        else:
            return JsonResponse({"status": 400, "error": "敏感词不存在"}, safe=False,json_dumps_params={'ensure_ascii': False})


class Delete_sensitive_word_prototype(APIView):
    """删除敏感词原型，点击叉号删除该原型，传入prototype，同时删除其所有变型"""
    def get(self,request):
        """人工删除敏感词：输入敏感词prototype;输出状态及提示：400 状态错误，201删除成功"""
        prototype = request.GET.get("prototype")
        result = SensitiveWord.objects.filter(prototype=prototype)
        if result.exists():
            try:
                SensitiveWord.objects.filter(prototype=prototype).delete()
                return JsonResponse({"status":201, "msg": "敏感词及其变型已删除"},safe=False,json_dumps_params={'ensure_ascii':False})
            except:
                return JsonResponse({"status":400, "error": "删除失败"},safe=False,json_dumps_params={'ensure_ascii':False})

        else:
            return JsonResponse({"status": 400, "error": "敏感词不存在"}, safe=False,json_dumps_params={'ensure_ascii': False})


class Show_global_parameter(APIView):
    """展示全局参数"""
    def get(self, request):
        """展示全局参数,返回GlobalParameter表中存在的需要展示的数据，其中返回的字段p_name为参数名称，p_value为参数的值"""
        result = SensitiveWord.objects.values('p_name', 'p_value')
        if result.exists():
            return HttpResponse(result)
        else:
            return JsonResponse({"status":400, "error": "无可显示的全局参数"},safe=False)
        json_data = serializers.serialize("json", result)
        results = json.loads(json_data)
        return JsonResponse(results, safe=False)


class Modify_global_parameter(APIView):
    """修改全局参数"""
    def get(self,request):
        """修改全局参数：输入参数名p_name,修改值p_value;输出状态及提示：400 状态错误，201写入成功"""
        p_name = request.GET.get("p_name")
        p_value = request.GET.get("p_value")
        #判断敏感词是否存在
        if p_name and p_value:
            result = GlobalParameter.objects.filter(p_name=p_name)
            if result.exists():
                GlobalParameter.objects.filter(p_name=p_name).update(p_value=p_value)
                return JsonResponse({"status":201, "msg": "参数成功修改"},safe=False,json_dumps_params={'ensure_ascii':False})
            else:
                return JsonResponse({"status": 400, "error": "参数不存在"}, safe=False,json_dumps_params={'ensure_ascii': False})

        else:
            return JsonResponse({"status":400, "error": "请输入全局参数和修改值"},safe=False,json_dumps_params={'ensure_ascii':False})
