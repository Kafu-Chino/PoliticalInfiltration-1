import os
import re
import time
import datetime
from collections import defaultdict
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum

from Config.time_utils import *
from Config.base import MSG_TYPE_DIC
from Informationspread.models import *
from Mainevent.models import Information

from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema

ABS_PATH = os.path.dirname(os.path.abspath(__file__))

class Sen_info(APIView):
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

class Show_Info(APIView):
    """展示信息传播态势接口"""

    def get(self, request):
        """
        获取微博mid，返回微博传播态势详情，可指定返回日期长度，默认为7天;
        返回格式: {date1:{spread_count_s:10},
                    date2:{spread_count_s: 10},
                    ...}
        """
        res_dict = {}
        mid = request.GET.get('mid')
        n = request.GET.get('n') if request.GET.get('n') else 7
        new_date = (datetime.datetime.now() + datetime.timedelta(days=-n)).timestamp()
        result = Informationspread.objects.filter(mid=mid, timestamp__gte=new_date).values(
            "timestamp").annotate(spread_count_s=Sum("spread_count"))
        for item in result:
            t = item.pop("timestamp") - 24 * 60 * 60
            res_dict[time.strftime("%Y-%m-%d", time.localtime(t))] = item
        return JsonResponse(res_dict)
