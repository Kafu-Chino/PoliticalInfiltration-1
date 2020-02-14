from django.shortcuts import render

# Create your views here.
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.core import serializers
import time

from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema
from .敏感词扩展.sensitive_word_extent import extent

from Systemmanage.models import *
from Mainevent.models import *


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
        if not result.exists():
            return JsonResponse({"status":400, "error": "无通用敏感词"},safe=False)
        else:
	        data = json.dumps(list(result))
	        results = json.loads(data)
	        return JsonResponse(results, safe=False)


class Show_sensitive_word_transform(APIView):
    """展示通用敏感词变型，点击敏感词传入prototype"""
    def get(self, request):
        prototype = request.GET.get("prototype")
        result = SensitiveWord.objects.filter(prototype=prototype).values('transform')
        if not result.exists():
            return JsonResponse({"status":400, "error": "无敏感词变型"},safe=False)
        else:
            data = json.dumps(list(result))
            results = json.loads(data)
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
                SensitiveWord.objects.create(s_id=str(times) + prototype, prototype=prototype, perspective_bias=0)
                transforms = extent(prototype)
                for transform in transforms:
                    SensitiveWord.objects.create(s_id=str(times)+transform, prototype=prototype, transform=transform, perspective_bias=0)
                return JsonResponse({"status":201, "msg": "敏感词成功添加"},safe=False,json_dumps_params={'ensure_ascii':False})
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
        result = GlobalParameter.objects.values('p_name', 'p_value', 'p_instruction')
        if not result.exists():
            return JsonResponse({"status":400, "error": "无可显示的全局参数"},safe=False)
        else:
            data = json.dumps(list(result))
            results = json.loads(data)
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




class Add_sensitiveword(APIView):
    """展示事件管理接口"""

    def get(self, request):
        """
        增加事件敏感词
        格式：{'word':word,'e_id':eid,'bias':bias}
        """
        res_dict = {}
        word = request.GET.get('word')
        e_id = request.GET.get('e_id')
        bias = request.GET.get('bias')
        try:
            SensitiveWord.objects.create(s_id=word + e_id, prototype=word, e_id=e_id, perspective_bias=bias)
            res_dict["status"] = 1
            res_dict["result"] = "添加成功"
        except:
            res_dict["status"] = 0
            res_dict["result"] = "添加失败"
        return JsonResponse(res_dict)

class Delete_sensitiveword(APIView):
    """展示事件管理接口"""

    def get(self, request):
        """
        删除敏感词
        格式：{'word':word,'e_id':eid}
        """
        res_dict = {}
        word = request.GET.get('word')
        e_id = request.GET.get('e_id')
        if SensitiveWord.objects.filter(prototype = word,e_id = e_id).exists():
            try:
                SensitiveWord.objects.filter(prototype = word,e_id = e_id).delete()
                res_dict["status"] = 1
                res_dict["result"] = "删除成功"
            except:
                res_dict["status"] = 0
                res_dict["result"] = "删除失败"
        else:
            res_dict["status"] = 0
            res_dict["result"] = "敏感词不存在"
        return JsonResponse(res_dict)


#敏感文本的添加和删除
class Add_sensitivetext(APIView):
    """展示事件管理接口"""

    def get(self, request):
        """
        增加事件敏感文本
        格式：{'i_id':i_id,'uid':uid,'mid':mid,'root_uid':root_uid,'root_mid':root_mid,'text':text,'timestamp':timestamp,
        'date':date,'send_ip':send_ip,'geo':geo,'message_type':message_type,'source':ource,'status':status}
        """
        res_dict = {}
        i_id = request.GET.get('i_id')
        uid = request.GET.get('uid')
        mid = request.GET.get('mid')
        root_uid = request.GET.get('root_uid')
        root_mid = request.GET.get('root_mid')
        text = request.GET.get('text')
        timestamp = request.GET.get('timestamp')
        send_ip = request.GET.get('send_ip')
        geo = request.GET.get('geo')
        message_type = request.GET.get('message_type')
        source = request.GET.get('source')
        # status = request.GET.get('status')
        try:
            Information.objects.create(i_id=i_id, uid=uid, root_uid=root_uid, mid=mid,root_mid=root_mid, timestamp=timestamp,
                                       text=text,send_ip=send_ip, geo=geo, message_type=message_type,source=source)
            res_dict["status"] = 1
            res_dict["result"] = "添加成功"
        except:
            res_dict["status"] = 0
            res_dict["result"] = "添加失败"
        return JsonResponse(res_dict)

class Delete_sensitivetext(APIView):
    """展示事件管理接口"""

    def get(self, request):
        """
        删除敏感文本
        格式：{'mid':mid}
        """
        res_dict = {}
        mid = request.GET.get('mid')
        if Information.objects.filter(mid = mid).exists():
            try:
                Information.objects.filter(mid = mid).delete()
                res_dict["status"] = 1
                res_dict["result"] = "删除成功"
            except:
                res_dict["status"] = 0
                res_dict["result"] = "删除失败"
        else:
            res_dict["status"] = 2
            res_dict["result"] = "信息不存在"
        return JsonResponse(res_dict)
#事件关键词的添加与删除
class Add_keyword(APIView):
    """展示事件管理接口"""

    def get(self, request):
        """
        增加事件关键词
        格式：{'word':word',e_id':e_id'}
        """
        res_dict = {}
        word = request.GET.get('word')
        e_id = request.GET.get('e_id')

        try:
            EventKeyWord.objects.create(k_id=word+e_id, word=word, e_id=e_id)
            res_dict["status"] = 1
            res_dict["result"] = "添加成功"
        except:
            res_dict["status"] = 0
            res_dict["result"] = "添加失败"
        return JsonResponse(res_dict)

class Delete_keyword(APIView):
    """展示事件管理接口"""

    def get(self, request):
        """
        删除事件关键词
        格式：{'word':word',e_id':e_id'}
        """
        res_dict = {}
        word = request.GET.get('word')
        e_id = request.GET.get('e_id')
        if EventKeyWord.objects.filter(k_id = word+e_id).exists():
            try:
                EventKeyWord.objects.filter(k_id = word+e_id).delete()
                res_dict["status"] = 1
                res_dict["result"] = "删除成功"
            except:
                res_dict["status"] = 0
                res_dict["result"] = "删除失败"
        else:
            res_dict["status"] = 0
            res_dict["result"] = "关键词不存在"
        return JsonResponse(res_dict)
#事件参数的添加更新
class Add_eventparameter(APIView):
    """展示事件管理接口"""

    def get(self, request):
        """
        增加事件关键词
        格式：{'p_name':p_name','p_value':p_value,'e_id':e_id}
        """
        res_dict = {}
        p_name = request.GET.get('p_name')
        e_id = request.GET.get('e_id')
        p_value = request.GET.get('p_value')

        try:
            EventParameter.objects.create(p_id = p_name+e_id,p_name=p_name, p_value=p_value, e_id=e_id)
            res_dict["status"] = 1
            res_dict["result"] = "添加成功"
            '''
            此处启动事件计算
            '''
        except:
            res_dict["status"] = 0
            res_dict["result"] = "添加失败"
        return JsonResponse(res_dict)

class Update_eventparameter(APIView):
    """展示事件管理接口"""

    def get(self, request):
        """
        更新事件关键词
        格式：{'p_name':p_name','e_id':e_id,'new_value':new_value}
        """
        res_dict = {}
        p_name = request.GET.get('p_name')
        e_id = request.GET.get('e_id')
        new_value = request.GET.get('new_value')
        if  EventParameter.objects.filter(p_name=p_name,e_id = e_id).exists():
            try:
                EventParameter.objects.filter(p_name=p_name,e_id = e_id).update(p_value = new_value)
                res_dict["status"] = 1
                res_dict["result"] = "更新成功"
                '''
                此处启动事件计算
                '''
            except:
                res_dict["status"] = 0
                res_dict["result"] = "更新失败"
        else:
            res_dict["status"] = 0
            res_dict["result"] = "参数不存在"
        return JsonResponse(res_dict)