import os
import re
from django.http import JsonResponse, HttpResponse

from Config.time_utils import *
from Config.base import MSG_TYPE_DIC
from Informationspread.models import Informationspread
from Mainevent.models import Information, Event

from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema

ABS_PATH = os.path.dirname(os.path.abspath(__file__))

class Show_Info(APIView):
    def get(self,request):
        mid = request.GET.get('mid')
        result = Information.objects.filter(mid=mid).values("uid",'text','timestamp','geo','message_type','hazard_index')
        res = {
            "uid": result[0]["uid"],
            "text": result[0]["text"],
            "time": ts2datetime(result[0]["timestamp"]),
            "geo": result[0]["geo"],
            "message_type": MSG_TYPE_DIC[result[0]["message_type"]]
        }
        if result[0]["hazard_index"]:
            res["hazard_index"] = result[0]["hazard_index"]
        else:
            res["hazard_index"] = "无"
        return JsonResponse(res,safe=False,json_dumps_params={'ensure_ascii':False})

class Trend(APIView):
    def get(self, request):
        mid = request.GET.get('mid')
        n = 90
        try:
            date = Event.objects.filter(information__mid=mid).order_by('end_date')[0].end_date.strftime('%Y-%m-%d')
        except:
            date = today()
        date = date2ts(date)
        date_before = date - n * 86400
        result = Informationspread.objects.filter(mid=mid, timestamp__gte=date_before, timestamp__lte=date).values()
        data_dic = {ts2date(item["timestamp"]): item["comment_count"] + item["retweet_count"] for item in result}
        print(data_dic)

        datelist = get_datelist_v2(ts2date(date_before), ts2date(date))
        count_list = []
        for date in datelist:
            if date in data_dic:
                count_list.append(data_dic[date])
            else:
                count_list.append(0)

        res_dict = {
            'date': datelist,
            'count': count_list
        }
        return JsonResponse(res_dict)
