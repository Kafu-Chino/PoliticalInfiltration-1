from django.shortcuts import render

# Create your views here.
import json
from xpinyin import Pinyin
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
        result = SensitiveWord.objects.filter(prototype=prototype).exclude(transform=None).values('transform')
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
                if len(prototype)<5:
                    transforms = extent(prototype)
                    for transform in transforms:
                        SensitiveWord.objects.create(s_id=str(times)+transform, prototype=prototype, transform=transform, perspective_bias=0)
                return JsonResponse({"status":201, "msg": "敏感词成功添加"},safe=False,json_dumps_params={'ensure_ascii':False})
            else:
                return JsonResponse({"status": 400, "error": "敏感词已存在"}, safe=False,json_dumps_params={'ensure_ascii': False})

        else:
            return JsonResponse({"status":400, "error": "请输入敏感词"},safe=False,json_dumps_params={'ensure_ascii':False})


class Add_sensitive_word_transform(APIView):
    """添加敏感词变型入库"""
    def get(self,request):
        """人工添加敏感词变型：传入敏感词原型prototype，变型transform;输出状态及提示：400 状态错误，201写入成功"""
        prototype = request.GET.get("prototype")
        transform = request.GET.get("transform")
        #判断参数是否传入
        if prototype and transform:
            result = SensitiveWord.objects.filter(prototype=prototype,transform=transform)
            if not result.exists():
                times = int(time.time())
                SensitiveWord.objects.create(s_id=str(times)+transform, prototype=prototype, transform=transform, perspective_bias=0)
                return JsonResponse({"status":201, "msg": "添加成功"},safe=False,json_dumps_params={'ensure_ascii':False})
            else:
                return JsonResponse({"status": 400, "error": "该变型已存在"}, safe=False,json_dumps_params={'ensure_ascii': False})

        else:
            return JsonResponse({"status":400, "error": "请输入敏感词变型"},safe=False,json_dumps_params={'ensure_ascii':False})


class Delete_sensitive_word_transform(APIView):
    """删除敏感词变型，点击叉号删除该变型，传入变型transform"""
    def get(self,request):
        """人工删除敏感词：输入敏感词变型transform;输出状态及提示：400 状态错误，201删除成功"""
        transform = request.GET.get("transform")
        result = SensitiveWord.objects.filter(transform=transform)
        if transform==None:
            return JsonResponse({"status": 400, "error": "敏感词变型不能为空"}, safe=False,json_dumps_params={'ensure_ascii': False})
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
        result = SensitiveWord.objects.filter(prototype=prototype, perspective_bias=0)
        if result.exists():
            try:
                SensitiveWord.objects.filter(prototype=prototype, perspective_bias=0).delete()
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

class Event_show(APIView):
    """事件列表展示"""

    def get(self, request):
        """
        展示所有事件，前端分页
        """
        result = Event.objects.all().filter(cal_status=2).order_by("-begin_date").values("e_id", "keywords_dict", "event_name", "begin_date", "end_date")
        res = [item for item in result]
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii':False})


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
    count = 0

    def get(self, request):
        """
        增加事件敏感文本
        格式：{'i_id':i_id,'uid':uid,'mid':mid,''text':text,'timestamp':timestamp,
        'date':date,'geo':geo,'message_type':message_type,'source':source,'e_id':e_id }
        """
        res_dict = {}
        uid = request.GET.get('uid')
        mid = request.GET.get('mid')
        text = request.GET.get('text')
        timestamp = request.GET.get('timestamp')
        geo = request.GET.get('geo')
        message_type = request.GET.get('message_type')
        source = request.GET.get('source')
        e_id = request.GET.get('e_id')
        if text == None:
            res_dict["status"] = 0
            res_dict["result"] = "添加失败,请输入信息文本内容"
            return JsonResponse(res_dict)
        if e_id == None:
            res_dict["status"] = 0
            res_dict["result"] = "添加失败,请输入信息所属事件"
            return JsonResponse(res_dict)
        if mid==None:
            mid = str(int(time.time()))
        if uid==None:
            uid = '手动添加'
        if source==None:
            source = '手动添加0'
        if timestamp==None:
            timestamp = 0
        if geo==None:
            geo = '无'
        if message_type==None:
            message_type = 0
        try:
        # Event.objects.filter(e_id=e_id).first().information_set.create(i_id=source+mid, uid=uid,  mid=mid, timestamp=timestamp,
        #                            text=text, geo=geo, message_type=message_type,source=source,add_manully = 1)
            if Information.objects.filter(mid=mid).exists():
                res_dict["status"] = 0
                res_dict["result"] = "添加失败,该mid已存在"
                return JsonResponse(res_dict)
            Information.objects.create(i_id=source+mid, uid=uid,  mid=mid, timestamp=timestamp,
                                       text=text, geo=geo, message_type=message_type,source=source,add_manully = 1)
            info =  Information.objects.get(i_id=source+mid)
            event = Event.objects.get(e_id = e_id)
            event.information.add(info)
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
        格式：{'mid':mid,'e_id':e_id}
        """
        res_dict = {}
        mid = request.GET.get('mid')
        e_id = request.GET.get('e_id')
        if Information.objects.filter(mid = mid).exists():
            try:
                info = Information.objects.get(mid = mid)
                event = Event.objects.get(e_id=e_id)
                event.information.remove(info)
                Information.objects.filter(mid=mid).delete()
                res_dict["status"] = 1
                res_dict["result"] = "删除成功"
            except:
                res_dict["status"] = 0
                res_dict["result"] = "删除失败"
        else:
            res_dict["status"] = 0
            res_dict["result"] = "信息不存在"
        return JsonResponse(res_dict)
#事件关键词的更新
class Update_eventkeyword(APIView):
    """展示事件管理接口"""

    def get(self, request):
        """
        更新事件关键词
        格式：{'e_id':e_id,'new_value':new_value}
        """
        res_dict = {}
        e_id = request.GET.get('e_id')
        new_value = request.GET.get('new_value')
        if  Event.objects.filter(e_id = e_id).exists():
            try:
                Event.objects.filter(e_id = e_id).update(keywords_dict = new_value)
                res_dict["status"] = 1
                res_dict["result"] = "更新成功"
            except:
                res_dict["status"] = 0
                res_dict["result"] = "更新失败"
        else:
            res_dict["status"] = 0
            res_dict["result"] = "该事件不存在关键词，请检查事件是否存在"
        return JsonResponse(res_dict)



#事件参数的更新
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


class Show_eventparameter(APIView):
    """展示事件管理接口"""

    def get(self, request):
        """
        展示事件参数
        格式：{'e_id':e_id}
        """
        e_id = request.GET.get('e_id')
        result = EventParameter.objects.filter(e_id=e_id).values('p_name', 'p_value', 'p_instruction')
        if not result.exists():
            return JsonResponse({"status": 400, "error": "该事件不存在参数，请检查事件是否正确"}, safe=False)
        else:
            data = json.dumps(list(result))
            results = json.loads(data)
            return JsonResponse(results, safe=False)


class Show_eventkeyword(APIView):
    """展示事件管理接口"""

    def get(self, request):
        """
        展示事件关键词
        格式：{'e_id':e_id}
        """
        e_id = request.GET.get('e_id')
        result = Event.objects.filter(e_id=e_id).values('keywords_dict')
        if not result.exists():
            return JsonResponse({"status": 400, "error": "该事件不存在关键词，请检查事件是否正确"}, safe=False)
        else:
            data = json.dumps(list(result))
            results = json.loads(data)
            return JsonResponse(results, safe=False)

class Show_eventsensitiveword(APIView):
    """展示事件管理接口"""

    def get(self, request):
        """
        展示事件关键词
        格式：{'e_id':e_id,'bias':bias}
        """
        e_id = request.GET.get('e_id')
        bias = request.GET.get('bias')
        result = SensitiveWord.objects.filter(e_id=e_id,perspective_bias=bias).values('prototype','perspective_bias')
        if not result.exists():
            return JsonResponse({"status": 400, "error": "该事件不存在此类敏感词，请检查事件是否正确"}, safe=False)
        else:
            data = json.dumps(list(result))
            results = json.loads(data)
            return JsonResponse(results, safe=False)

class Show_sensitivetext(APIView):
    """展示事件管理接口"""

    def get(self, request):
        """
        展示事件敏感信息
        格式：{'add_manully':add_manully,'e_id':e_id}
        """
        # add_manully = request.GET.get('add_manully')
        e_id = request.GET.get('e_id')
        event_obj = Event.objects.get(e_id=e_id)
        info = event_obj.information.filter(add_manully = 1)
        result = info.values("text")

        # results = information_id.information_set.all()
        if not result.exists():
            return JsonResponse({"status": 400, "error": "该事件不存在敏感文本，请检查事件是否正确"}, safe=False)
        else:
            data = json.dumps(list(result))
            results = json.loads(data)
            return JsonResponse(results, safe=False)

class Recal_event(APIView):
    """展示事件管理接口"""

    def get(self, request):
        e_id = request.GET.get("e_id")

        # Event表的迁移
        event_obj = Event.objects.get(e_id=e_id)

        event_name_pinyin = Pinyin().get_pinyin(event_obj.event_name, '')
        e_id_new = "{}_{}".format(event_name_pinyin, str(int(time.time())))
        Event.objects.create(
            e_id=e_id_new,
            event_name=event_obj.event_name,
            keywords_dict=event_obj.keywords_dict,
            begin_date=event_obj.begin_date,
            end_date=event_obj.end_date,
            es_index_name=e_id_new,
            cal_status=0,
            monitor_status=1
        )

        # 敏感词、事件参数、人工扩线信息直接换id和内容
        sensitiveword = SensitiveWord.objects.filter(e_id=e_id)
        for item in sensitiveword:
            item.e_id = e_id_new
            item.s_id = item.prototype + e_id_new
            item.save()

        eventparameter = EventParameter.objects.filter(e_id=e_id)
        for item in eventparameter:
            item.e_id = e_id_new
            item.p_id = item.p_name + e_id_new
            item.save()

        event_obj = Event.objects.get(e_id=e_id)
        information = event_obj.information.filter(add_manully=1)
        event_new_obj = Event.objects.get(e_id=e_id_new)
        for item in information:
            event_new_obj.information.add(item)

        return JsonResponse({"status": 200, "info": "事件重新计算任务创建成功，请到任务列表查看。"}, safe=False)