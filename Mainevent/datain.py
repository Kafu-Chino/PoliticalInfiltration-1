from django.http import JsonResponse,HttpResponse
from django.db.models import Q
from Mainevent.models import Task
import json
import time
import datetime


# task_type 0->NewEvent 1->RelativeEvent
# into_type 0->manually add 1->from push 2->system add automatically
# status 0->waiting for computing 1->already computed 2->computing 3->failed to compute

def add_by_input(request):
    times = int(time.time())
    dates = datetime.datetime.now().strftime('%Y-%m-%d')  # 获取当前时间戳和日期
    if request.method == 'POST':
        event = request.POST       
        event_id = event["name"] + str(times)  # 事件名+时间戳作为任务ID
        event_content = event["content"]  # 获取事件内容
        keywords = event["keywords"]  # 获取事件关键词
        h_id = event["wb_id"]  #获取微博ID 可为空
    if request.method == 'GET':
        event_id = str(request.GET.get("name")) + str(times)
        event_content = request.GET.get("content")
        keywords = request.GET.get("keywords")
        h_id = request.GET.get("wb_id")
    result = Task.objects.filter(~Q(mid=''), mid=h_id) #判断从微博得来的事件是否已存在，若微博ID未给出返回一个空值
    if event_id and keywords and event_content:
        if result.exists():
            return JsonResponse({"msg": "Event already exists"})
        else:
           Task.objects.create(t_id=event_id, task_type="0", into_type="0", status=0, text=event_content,keywords_dict=keywords, mid=h_id,into_timestamp=times,
                               into_date=dates)
           return JsonResponse({"msg": "add successfully"})
    else:
        return HttpResponse("please input valid data")


def add_from_push(request):
    if request.method == 'GET':
        event_id = request.GET.get('mid')  # 从推送得到微博ID
        relative_id = request.GET.get("rmid")  # 若作为相关事件入库，获取相关事件的ID，目前设定只有一个相关事件
#        relative_id = ','.join(relative_ids)  
        times = time.time()
        keywords = request.GET.get("keywords_dict")
        dates = datetime.datetime.now().strftime('%Y-%m-%d')
        result = Task.objects.filter(mid=event_id)
        if result.exists():
            return JsonResponse({"msg": "Event already exists"})
        elif relative_id == "":  #判断是否选中了相关事件,若未选中，其rmid为空
            Task.objects.create(t_id=event_id, task_type="0", into_type="1", status="0", keywords_dict=keywords, into_timestamp=times, into_date=dates)
            return JsonResponse({"msg": "add successfully"})
        else:
            Task.objects.create(t_id=event_id, task_type="1", into_type="1", e_id=relative_id, status="0", keywords_dict=keywords, into_timestamp=times, into_date=dates)
            return JsonResponse({"msg": "add to relatives successfully"})


'''def add_to_relatives(request):
    if request.method == 'GET':
        event_id = request.GET.get('mid')
        times = time.time()      
        event_content =request.GET.get('text')
        keywords = request.GET.get('keywords_dict')
        dates = datetime.date()
        result = Task.objects.filter(mid=event_id)
        if result.exits():
            return JsonResponse({"msg": "Event already exits"})
        else:
            add_ev = Task(t_id=event_id, task_type="RelativeEvent", into_type="FromPush", status=0, text=event_content,
                          keywords_dict=keywords, into_timestamp=times,into_date=dates)
            add_ev.save()
            return JsonResponse({"msg": "add successfully"})'''


def add_by_system(request):
    # algorithm decide weather to add
    pass
