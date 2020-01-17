# -*- coding: utf-8 -*-
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.db.models import Q
from Mainevent.models import Task
import json
import time,datetime


from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema

from Mainevent.models import Hot_post

class Test(APIView):
    """测试页面"""
'''    def get(self, request):
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
        pass'''


class AddByInput(APIView):
    """手动添加事件入库"""
# task_type 0->新事件入库 1->作为相关事件入库
# into_type 0->人工手动添加 1->从热贴推送入库 2->系统计算入库
# status 0->未计算 1->已计算 2->计算中 3->计算失败
    def post(self,request):
        """人工添加事件：获取添加信息，输入name,keywords,content,wb_id调取事件名称、关键词和内容，输出状态及提示：400 状态错误，201写入成功"""
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
        """人工添加事件：获取添加信息，输入name,keywords,content,wb_id调取事件名称、关键词、内容和微博ID，若没有填写微博ID则wb_id="";输出状态及提示：400 状态错误，201写入成功"""
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
        """业务员选择推出热贴入库，输入mid(微博id)，rmid(相关事件id），keywords_dict(关键词），输出状态码和提示：400 状态错误，201写入成功
           当业务员点击事件入库但没有点击相关事件时，按钮返回该热帖的ID、关键词和相关事件ID,字段名分别为mid，keywords_dict(字符串格式：关键词1,关键词2,关键词3...各关键词中间用英文逗号分隔开）、rmid，所返回rmid为空
           当业务员选中了相关事件并点击按钮进行事件入库时，返回按钮返回该热帖的ID、关键词和相关事件ID,字段名分别为mid，keywords_dict(字符串、列表、数组格式均可）、rmid"""
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
        """展示任务列表,该文档返回Task表中存在的需要展示的数据，其中返回的字段keywords_dict作为事件名称(暂时以关键词作为名称)，
           into_date为添加时间，task_type为计算状态，若返回0则未计算，1为已计算，2为计算中，3为计算失败"""
        result = Task.objects.filter(keywords_dict,into_date,task_type)
        json_data = serializers.serialize("json",result)
        results = json.loads(json_data)
        return JsonResponse(results,safe=False)


class push_Hotpost(APIView):
    """页面响应,从数据库取热帖展示"""
    def get(self):
        hot_posts = Hot_post.objects.all().values_list()  # 取出所有列，QuerySet类型
        hot_posts = list(hot_posts)  # [(data),(data)]
        # 元组(data):
        # (h_id, uid, root_uid, mid, comment, retweeted, text, keywords_dict, timestamp, date, ip, geo, message_type, root_mid, source, store_timestamp, store_date, similar_event)
        # 例如:
        # ('h_1', 'user_1', 'user_1', 'm_1', 0, 0, '测试热帖库信息', 't1,t2,t3,t4,t5', 1567923180, datetime.date(2019, 9, 8), '127.0.0.1', '北京市', 1, 'm_1', '微博', 1567925639, datetime.date(2019, 9, 8), None)
        hot_post_display = []
        for item in hot_posts:
            a_post = {}
            a_post["h_id"] = item[0]
            a_post["uid"] = item[1]
            a_post["root_uid"] = item[2]
            a_post["mid"] = item[3]
            a_post["comment"] = item[4]
            a_post["retweeted"] = item[5]
            a_post["text"] = item[6]
            a_post["keywords_dict"] = item[7]
            a_post["timestamp"] = item[8]
            a_post["date"] = item[9].strftime('%Y-%m-%d')
            a_post["ip"] = item[10]
            a_post["geo"] = item[11]
            a_post["message_type"] = item[12]
            a_post["root_mid"] = item[13]
            a_post["source"] = item[14]
            a_post["store_timestamp"] = item[15]
            a_post["store_date"] = item[16].strftime('%Y-%m-%d')
            a_post["similar_event"] = item[17]
            hot_post_display.append(a_post)
        results = json.dumps(hot_post_display)
        return JsonResponse(results, safe=False)  # json [{data},{data}]


class Person_show(APIView):
    """用户主表展示"""
    def get(self, request):
        """
        用户展示大表信息
        输入：
        pagenum：当前页码数（以1起始）
        pagelimit：每页显示个数
        输出：
        uid：用户id
        nick_name：人物昵称
        create_at：注册时间
        user_location：注册地点
        fansnum：粉丝数
        friendsnum：关注数
        information_num：发布敏感信息数
        events_name：相关渗透事件
        """
        page_num = int(request.GET.get('pagenum', 1)) - 1
        page_limit = int(request.GET.get('pagelimit', 10))
        persons = Figure.objects.all()[page_num * page_limit : (page_num + 1) * page_limit]
        results = []

        # 批量得到用户相关信息统计
        persons_uid = [p.uid for p in persons]
        informations = Information.objects.filter(uid__in=persons_uid)
        information_count = {uid:0 for uid in persons_uid}
        for i in informations:
            information_count[i.uid] += 1

        # 批量得到用户相关事件统计
        events = Event.objects.filter(figure__uid__in=persons_uid).values_list("event_name", "figure__uid")
        events_name = {uid:[] for uid in persons_uid}
        for e in events:
            event_name, uid = e
            events_name[uid].append(event_name)

        for person in persons:
            dic = {
                "uid":person.uid,
                "nick_name":person.nick_name,
                "create_at":ts2date(int(person.create_at)),
                "user_location":person.user_location,
                "fansnum":person.fansnum,
                "friendsnum":person.friendsnum,
                "information_num":information_count[person.uid],
                "events_name":events_name[person.uid]
            }
            results.append(dic)
        return JsonResponse(results, safe=False)
