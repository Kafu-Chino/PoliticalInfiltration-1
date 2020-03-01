import os
import re
from django.http import JsonResponse, HttpResponse

from Config.time_utils import *
from Config.db_utils import get_global_para
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
        try:
            date = Event.objects.filter(information__mid=mid).order_by('end_date')[0].end_date.strftime('%Y-%m-%d')
        except:
            date = today()
        date = date2ts(date)
        mid_item = Information.objects.filter(mid=mid).values()
        date_before = mid_item[0]["timestamp"]
        if date_before:
            date_before = date2ts(ts2date(date_before))
        else:
            date_before = date - 30 * 86400
        date_before = date - 90 * 86400

        result = Informationspread.objects.filter(mid=mid, timestamp__gte=date_before, timestamp__lte=date).values()
        data_dic = {ts2date(item["timestamp"]): item["comment_count"] + item["retweet_count"] for item in result}

        if len(result):
            message_type = result[0]["message_type"]
        else:
            message_type = 1

        datelist = get_datelist_v2(ts2date(date_before), ts2date(date))
        decay_ratio = get_global_para("information_trend_decay_ratio")
        count_list = []
        for date in datelist:
            if date in data_dic:
                if message_type == 1:
                    count_list.append(data_dic[date])
                elif message_type in [2,3]:
                    count_list.append(int(data_dic[date] * decay_ratio))
            else:
                count_list.append(0)

        res_dict = {
            'date': datelist,
            'count': count_list
        }
        return JsonResponse(res_dict)
