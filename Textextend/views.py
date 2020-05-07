from django.shortcuts import render


import json
from xpinyin import Pinyin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.core import serializers
import time
from bert_serving.client import BertClient

from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema

from Cron.event_cal.sensitivity import bert_vec
from Config.base import BERT_HOST, BERT_PORT, BERT_PORT_OUT
from Textextend.models import *
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


def bert_vec(texts):
    with BertClient(ip=BERT_HOST, port=BERT_PORT, port_out=BERT_PORT_OUT) as bc:
        vec = bc.encode(texts)
        vec = list(vec)
    return vec


class Add_sensitivetext(APIView):
    count = 0

    def get(self, request):
        """
        增加事件敏感文本
        格式：{'e_id':e_id,'text':text }
        """
        res_dict = {}
        text = request.GET.get('text')
        texts = [text]
        e_id = request.GET.get('e_id')
        try:
            if EventPositive.objects.filter(text=text,e_id=e_id).exists():
                res_dict["status"] = 0
                res_dict["result"] = "添加失败,该条扩线信息已存在"
                return JsonResponse(res_dict)
            # print (texts)
            vector = bert_vec(texts)[0].tostring()
            # print(vector)

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
        new_result = []
        for i in result:
            new_result.append({'text':i['text'],'time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i['store_timestamp']))})
        # if not result.exists():
        #     return JsonResponse({"status": 400, "error": "该事件不存在，请检查事件是否正确"}, safe=False)
        # else:
        data = json.dumps(list(new_result))
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
        if EventPositive.objects.filter(e_id=e_id,text=text).exists():
            EventPositive.objects.filter(e_id=e_id,text=text).delete()
        else:
            return JsonResponse({"status": 400, "result": "文本不存在 "}, safe=False)
        return JsonResponse({"status": 1, "result": "删除成功 "}, safe=False)

class Deletemulti_sensitivetext(APIView):

    def get(self, request):
        """
        批量删除
        格式：{'e_id':e_id,'text':text}
        """
        e_id = request.GET.get('e_id')
        texts = request.GET.get('text').split('$')
        for text in texts:
            if EventPositive.objects.filter(e_id=e_id,text=text).exists():
                EventPositive.objects.filter(e_id=e_id,text=text).delete()
            else:
                # return JsonResponse({"status": 1, "result": "文本不存在 "}, safe=False)
                continue
        return JsonResponse({"status": 1, "result": "删除成功 "}, safe=False)

class Submit_extent(APIView):

    def get(self, request):
        """
        展示事件关键词
        格式：{'e_id':e_id}
        """
        e_id = request.GET.get('e_id')
        if ExtendTask.objects.filter(e_id=e_id).exists():
            ExtendTask.objects.filter(e_id=e_id).update(cal_status=0)
        else:
            ExtendTask.objects.create(e_id=e_id,cal_status=0)
        return JsonResponse({"status": 1, "result": "提交成功 "}, safe=False)

class Show_seedtext(APIView):
    def get(self, request):
        """
        展示种子文本
        格式：{'e_id':e_id}
        """
        e_id = request.GET.get('e_id')
        result = EventPositive.objects.filter(e_id=e_id).values('text','store_timestamp','store_type')
        new_result = []
        for i in result:
            new_result.append(
                {'text': i['text'], 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i['store_timestamp'])),'store_type':i['store_type']})
        if not result.exists():
            return JsonResponse({"status": 400, "error": "该事件不存在种子信息，请检查事件是否正确"}, safe=False)
        else:
            data = json.dumps(list(new_result))
            results = json.loads(data)
            return JsonResponse(results, safe=False)

class Show_audittext(APIView):
    def get(self, request):
        """
        展示种子文本
        格式：{'e_id':e_id}
        """
        e_id = request.GET.get('e_id')
        result = ExtendReview.objects.filter(e_id=e_id,process_status=0).values('text')
        if not result.exists():
            return JsonResponse({"status": 400, "error": "该事件不存在待审核信息，请检查事件是否正确"}, safe=False)
        else:
            print (result)
            data = json.dumps(list(result))
            results = json.loads(data)
            return JsonResponse(results, safe=False)

class Delete_audittext(APIView):

    def get(self, request):
        """
        删除种子文本
        格式：{'e_id':e_id,'text':text}
        """
        e_id = request.GET.get('e_id')
        text = request.GET.get('text')
        if ExtendReview.objects.filter(e_id=e_id,text=text).exists():
            ExtendReview.objects.filter(e_id=e_id,text=text).delete()
        else:
            return JsonResponse({"status": 0, "result": "文本不存在 "}, safe=False)
        return JsonResponse({"status": 1, "result": "删除成功 "}, safe=False)

class Delete_seedtext(APIView):

    def get(self, request):
        """
        删除种子文本
        格式：{'e_id':e_id,'text':text}
        """
        e_id = request.GET.get('e_id')
        text = request.GET.get('text')
        if EventPositive.objects.filter(e_id=e_id,text=text).exists():
            EventPositive.objects.filter(e_id=e_id,text=text).delete()
        else:
            return JsonResponse({"status": 0, "result": "文本不存在 "}, safe=False)
        return JsonResponse({"status": 1, "result": "删除成功 "}, safe=False)

class Deletemulti_seedtext(APIView):

    def get(self, request):
        """
        批量删除
        格式：{'e_id':e_id,'text':text}
        """
        e_id = request.GET.get('e_id')
        texts = request.GET.get('text').split('$')
        for text in texts:
            if EventPositive.objects.filter(e_id=e_id,text=text).exists():
                EventPositive.objects.filter(e_id=e_id,text=text).delete()
            else:
                # return JsonResponse({"status": 1, "result": "文本不存在 "}, safe=False)
                continue
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

            ExtendReview.objects.filter(text=text).update(process_status=1)
            vector = bert_vec([text])[0].tostring()
            timestamp = int(time.time())
            EventPositive.objects.create(store_timestamp=timestamp,text=text, e_id=e_id,store_type=2,process_status=0,vector=vector)
            result = ExtendReview.objects.filter(text=text).values()[0]
            # print (result)
            Information.objects.create(i_id=result['source']+result['mid'],uid=result['uid'],root_uid=result['root_uid'],mid = result['mid'],
                                       root_mid = result['root_mid'],text=text,timestamp=result['timestamp'],
                                       send_ip=result['send_ip'],geo=result['geo'],message_type=result['message_type']
                                       ,source=result['source'],cal_status=0,add_manully=1)
            # Event_information.objects.create(information_id=result['source'] + result['mid'], event_id=e_id)
            info = Information.objects.get(i_id=result['source']+result['mid'])
            event = Event.objects.get(e_id=e_id)
            event.information.add(info)
            res_dict["status"] = 1
            res_dict["result"] = "提交成功"
        except:
            res_dict["status"] = 0
            res_dict["result"] = "添加失败"
        return JsonResponse(res_dict)

class Addmulti_audittext(APIView):
    count = 0

    def get(self, request):
        """
        增加事件敏感文本
        格式：{'e_id':e_id,'text':text }
        """
        res_dict = {}
        texts = request.GET.get('text').split('$')
        e_id = request.GET.get('e_id')
        for text in texts:
            try:
                if not ExtendReview.objects.filter(text=text).exists():
                    # res_dict["status"] = 0
                    # res_dict["result"] = "添加失败,该条扩线信息不存在"
                    # return JsonResponse(res_dict)
                    continue
                ExtendReview.objects.filter(text=text).update(process_status=1)
                vector = bert_vec([text])[0].tostring()
                timestamp = int(time.time())
                EventPositive.objects.create(store_timestamp=timestamp,text=text, e_id=e_id,store_type=2,process_status=0,vector=vector)
                result = ExtendReview.objects.filter(text=text).values()[0]
                # print (result)
                Information.objects.create(i_id=result['source']+result['mid'],uid=result['uid'],root_uid=result['root_uid'],mid = result['mid'],
                                           root_mid = result['root_mid'],text=text,timestamp=result['timestamp'],
                                           send_ip=result['send_ip'],geo=result['geo'],message_type=result['message_type']
                                           ,source=result['source'],cal_status=0,add_manully=1)
                # Event_information.objects.create(information_id=result['source']+result['mid'],event_id=e_id)
                info = Information.objects.get(i_id=result['source'] + result['mid'])
                event = Event.objects.get(e_id=e_id)
                event.information.add(info)
            except:
                continue
        # res_dict["status"] = 0
        # res_dict["result"] = "添加失败"
        res_dict["status"] = 1
        res_dict["result"] = "提交成功"
        return JsonResponse(res_dict)


class Check(APIView):
    """扩线检查状态接口"""
    def get(self, request):
        """检查状态接口"""
        e_id = request.GET.get("e_id")
        result = ExtendTask.objects.filter(e_id=e_id).values('cal_status')
        if not result.exists():
            return JsonResponse({"status":200, "info": "允许操作"},safe=False)
        else:
            if result[0]['cal_status'] == 3:
                return JsonResponse({"status": 200, "info": "允许操作"}, safe=False)
            else:
                return JsonResponse({"status": 400, "info": "不允许操作"}, safe=False)


class Process(APIView):
    """处理完毕接口"""
    def get(self, request):
        e_id = request.GET.get("e_id")
        result = ExtendTask.objects.filter(e_id=e_id).values('cal_status')
        if not result.exists():
            return JsonResponse({"status":400, "error": "请先提交扩线任务"},safe=False)
        else:
            if result[0]['cal_status'] == 3:
                return JsonResponse({"status": 400, "error": "请先提交扩线任务"}, safe=False)
            else:
                EventPositive.objects.filter(e_id=e_id, store_type=1).update(process_status=1)
                ExtendReview.objects.filter(e_id=e_id, process_status=0).update(process_status=1)
                return JsonResponse({"status": 200, "info": "当前扩线任务已处理完毕"}, safe=False)