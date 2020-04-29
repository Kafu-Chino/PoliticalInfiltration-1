from django.shortcuts import render


import json
from xpinyin import Pinyin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.core import serializers
import time

from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema

from Cron.event_cal.sensitivity import bert_vec
from Textxtent.models import *
from Mainevent.models import *
# Create your views here.

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


class Add_sensitivetext(APIView):
    count = 0

    def get(self, request):
        """
        增加事件敏感文本
        格式：{'e_id':e_id,'text':text }
        """
        res_dict = {}
        text = request.GET.get('text')
        e_id = request.GET.get('e_id')
        try:
            if EventPositive.objects.filter(text=text,e_id=e_id).exists():
                res_dict["status"] = 0
                res_dict["result"] = "添加失败,该条扩线信息已存在"
                return JsonResponse(res_dict)
            vector = bert_vec([text])[0].tostring()
            timestamp = int(time.time())
            EventPositive.objects.create(store_timestamp=timestamp,text=text, e_id=e_id,store_type=1,process_status=0,vector=vector)
            res_dict["status"] = 1
            res_dict["result"] = "添加成功"
        except:
            res_dict["status"] = 0
            res_dict["result"] = "添加失败"
        return JsonResponse(res_dict)

class Show_sensitivetext(APIView):

    def get(self, request):
        """
        展示事件关键词
        格式：{'e_id':e_id}
        """
        e_id = request.GET.get('e_id')
        result = EventPositive.objects.filter(e_id=e_id,store_type=1,process_status=0).values('text','store_timestamp')
        if not result.exists():
            return JsonResponse({"status": 400, "error": "该事件不存在，请检查事件是否正确"}, safe=False)
        else:
            data = json.dumps(list(result))
            results = json.loads(data)
            return JsonResponse(results, safe=False)

class Delete_sensitivetext(APIView):

    def get(self, request):
        """
        展示事件关键词
        格式：{'e_id':e_id,'text':text}
        """
        e_id = request.GET.get('e_id')
        text = request.GET.get('text')
        EventPositive.objects.filter(e_id=e_id,text=text).delete()
        return JsonResponse({"status": 1, "result": "删除成功 "}, safe=False)

class Submit_extent(APIView):

    def get(self, request):
        """
        展示事件关键词
        格式：{'e_id':e_id}
        """
        e_id = request.GET.get('e_id')
        if ExtendTask.objects.filter(e_id=e_id).exists():
            ExtendTask.objects.filter(e_id=e_id).update(cal_status=1)
        else:
            ExtendTask.objects.create(e_id=e_id,cal_status=1)
        return JsonResponse({"status": 1, "result": "提交成功 "}, safe=False)

class Show_seedtext(APIView):
    def get(self, request):
        """
        展示种子文本
        格式：{'e_id':e_id}
        """
        e_id = request.GET.get('e_id')
        result = EventPositive.objects.filter(e_id=e_id).values('text','store_timestamp','store_type')
        if not result.exists():
            return JsonResponse({"status": 400, "error": "该事件不存在种子信息，请检查事件是否正确"}, safe=False)
        else:
            data = json.dumps(list(result))
            results = json.loads(data)
            return JsonResponse(results, safe=False)


class Delete_seedtext(APIView):

    def get(self, request):
        """
        删除种子文本
        格式：{'e_id':e_id,'text':text}
        """
        e_id = request.GET.get('e_id')
        text = request.GET.get('text')
        EventPositive.objects.filter(e_id=e_id,text=text).delete()
        return JsonResponse({"status": 1, "result": "删除成功 "}, safe=False)

class Add_audittext(APIView):
    count = 0

    def get(self, request):
        """
        增加事件敏感文本
        格式：{'e_id':e_id,'text':text }
        """
        res_dict = {}
        text = request.GET.get('text')
        e_id = request.GET.get('e_id')
        try:
            if not ExtendReview.objects.filter(text=text).exists():
                res_dict["status"] = 0
                res_dict["result"] = "添加失败,该条扩线信息不存在"
                return JsonResponse(res_dict)


            vector = bert_vec([text])[0].tostring()
            timestamp = int(time.time())
            EventPositive.objects.create(store_timestamp=timestamp,text=text, e_id=e_id,store_type=1,process_status=0,vector=vector)
            result = ExtendReview.objects.filter(text=text).first()
            print (result)
            Information.objects.create(uid=result['uid'],root_uid=result['root_uid'],mid = result['mid'],
                                       root_mid = result['root_mid'],text=text,timestamp=result['timestamp'],
                                       send_ip=result['send_ip'],geo=result['geo'],message_type=result['message_type']
                                       ,source=result['source'],cal_status=0,add_manully=1)
            res_dict["status"] = 1
            res_dict["result"] = "添加成功"
        except:
            res_dict["status"] = 0
            res_dict["result"] = "添加失败"
        return JsonResponse(res_dict)







