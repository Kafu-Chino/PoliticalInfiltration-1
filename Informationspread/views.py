import os
import re
from django.http import JsonResponse, HttpResponse

from Config.time_utils import *
from Config.db_utils import get_global_para
from Config.base import MSG_TYPE_DIC
from Informationspread.models import Informationspread
from Mainevent.models import Information, Event
from collections import defaultdict

from itertools import chain

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
            res["hazard_index"] = int(result[0]["hazard_index"])
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

class Info_spread(APIView):
    """信息传播势态接口"""

    def get(self, request):
        """
        获取mid，返回信息的传播预测

        """
        mid = request.GET.get('mid')
        date = Informationspread.objects.filter(mid=mid).exclude(predict=1).order_by('-store_date')[0].store_date.strftime('%Y-%m-%d')
        date2 = Informationspread.objects.filter(mid=mid).exclude(predict=1).order_by('store_date')[0].store_date.strftime('%Y-%m-%d')
        res_dict = defaultdict(dict)
        # date = date2ts(date)

        dl = get_datelist_v2(date2, date)
        for d in dl:
            result =  Informationspread.objects.filter(mid=mid, store_date__gte=d, store_date__lte=d).values('retweet_count','comment_count')
            if result.exists():
                res_dict['retweet_count'][d] = result[0]['retweet_count']
                res_dict['comment_count'][d] = result[0]['comment_count']

            else:
                res_dict['retweet_count'][d] = 0
                res_dict['comment_count'][d] = 0

        n_res = defaultdict(dict)
        n_res['date'] = list(res_dict['retweet_count'].keys())
        n_res['retweet_count']=[]
        for i in range(len( list(res_dict['retweet_count'].values()))):
            n_res['retweet_count'].append(list(res_dict['retweet_count'].values())[i]+list(res_dict['comment_count'].values())[i])
        # n_res['retweet_count'] = list(res_dict['retweet_count'].values())#.extend(['-','-'])
        n_res['retweet_count'].extend(['-','-'])
        # n_res['comment_count'] = list(res_dict['comment_count'].values())
        # n_res['comment_count'].extend(['-','-'])
        # print(n_res['retweet_count'])
        date = Informationspread.objects.filter(mid=mid,predict=1).order_by('-store_date')[
            0].store_date.strftime('%Y-%m-%d')
        date2 = Informationspread.objects.filter(mid=mid,predict=1).order_by('store_date')[
            0].store_date.strftime('%Y-%m-%d')
        dl = get_datelist_v2(date2, date)
        for d in dl:
            result =  Informationspread.objects.filter(mid=mid, store_date__gte=d, store_date__lte=d).values('retweet_count','comment_count')
            if result.exists():
                res_dict['retweet_count_pred'][d] = result[0]['retweet_count']
                res_dict['comment_count_pred'][d] = result[0]['comment_count']

            else:
                res_dict['retweet_count_pred'][d] = 0
                res_dict['comment_count_pred'][d] = 0

        n_res['date'].extend(dl)
        n_res['retweet_count_pred'] = []
        # n_res['comment_count_pred'] = []
        for i in range(len(res_dict['retweet_count'].values())-1):
            n_res['retweet_count_pred'].append('-')
            # n_res['comment_count_pred'].append('-')
        print (res_dict['retweet_count'])
        n_res['retweet_count_pred'].append(n_res['retweet_count'][len(res_dict['retweet_count'].values())-1])
        # n_res['comment_count_pred'].append(list(res_dict['comment_count'].values())[len(res_dict['retweet_count'].values())-1])
        for i in range(len(res_dict['retweet_count_pred'])):
            n_res['retweet_count_pred'].append(list(res_dict['retweet_count_pred'].values())[i]+list(res_dict['comment_count_pred'].values())[i])
        # n_res['retweet_count_pred'].extend(list(res_dict['retweet_count_pred'].values()))
        # n_res['comment_count_pred'].extend(list(res_dict['comment_count_pred'].values()))
        # normal_days = len(n_res['retweet_count'])

        print(n_res['date'])
        n_res['retweet_name'] = []
        n_res['retweet_pieces'] = []
        change_point = []
        for i in range(len(n_res['date'])):
            # print(n_res['retweet_count'])
            if n_res['retweet_count'][i] != '-':
                if n_res['retweet_count'][i]>1000:
                    change_point.append(1)
                else:
                    change_point.append(0)
            else:
                if n_res['retweet_count_pred'][i]>1000:
                    change_point.append(1)
                else:
                    change_point.append(0)
        big_check_point =[]
        small_check_point = []
        date_list = n_res['date']
        for i in range(1,len(n_res['date'])):
            if change_point[i] > change_point[i-1]:
                big_check_point.append(i)
            elif change_point[i] < change_point[i-1]:
                small_check_point.append(i)
        if len(big_check_point)==0:
            if len(small_check_point)==0:
                if  n_res['retweet_count'][0]>1000:
                    n_res['retweet_pieces'].append({'lte': len(date_list)-1,'gt':0, 'color': 'red'})
                    n_res['retweet_name'].append(
                        [{'name': '预警', 'xAxis': date_list[0]}, {'xAxis': date_list[len(date_list)-1]}])
                else:
                    n_res['retweet_pieces'].append(
                        {'lte': len(date_list) - 1, 'gt': 0, 'color': 'green'})
            else:
                n_res['retweet_pieces'].append({'lte': small_check_point[0],'gt':0, 'color': 'red'})
                n_res['retweet_pieces'].append({'lte': len(date_list)-1,'gt':small_check_point[0], 'color': 'green'})
                n_res['retweet_name'].append(
                    [{'name': '预警', 'xAxis': date_list[0]}, {'xAxis': date_list[small_check_point[0]]}])

        if len(big_check_point)!=0:
            if len(small_check_point) == 0:
                n_res['retweet_pieces'].append(
                    {'lte': big_check_point[0], 'gt': 0, 'color': 'green'})
                n_res['retweet_pieces'].append({'lte': len(date_list)-1, 'gt': big_check_point[0], 'color': 'red'})
                n_res['retweet_name'].append(
                    [{'name': '预警', 'xAxis': date_list[big_check_point[0]]}, {'xAxis': date_list[-1]}])

        if len(big_check_point)!=0 and len(small_check_point)!=0:
            if big_check_point[0] <small_check_point[0]:
                if len(big_check_point)>len(small_check_point):
                    n_res['retweet_pieces'].append({'lte': big_check_point[0], 'color': 'green'})
                    color_point = []
                    color_point.extend(list(chain.from_iterable(zip(big_check_point[:-1], small_check_point))).append(big_check_point[-1]))
                    for i in range(1,len(color_point)):
                        if i%2==1:
                            n_res['retweet_pieces'].append({'lte': color_point[i],'gt':color_point[i-1], 'color': 'red'})
                            n_res['retweet_name'].append([{'name':'预警','xAxis':date_list[color_point[i-1]]},{'xAxis':date_list[color_point[i]]}])
                        else:
                            n_res['retweet_pieces'].append({'lte': color_point[i],'gt':color_point[i-1], 'color': 'green'})
                    n_res['retweet_pieces'].append({'gt':color_point[i], 'color': 'red'})
                    n_res['retweet_name'].append([{'name': '预警', 'xAxis': date_list[color_point[i]]}, {'xAxis': date_list[len(n_res['date'])-1]}])
                else:
                    n_res['retweet_pieces'].append({'lte': big_check_point[0], 'color': 'green'})
                    color_point = []
                    color_point.extend(
                        list(chain.from_iterable(zip(big_check_point, small_check_point))))
                    for i in range(1, len(color_point)):
                        if i % 2 == 1:
                            n_res['retweet_pieces'].append({'lte': color_point[i], 'gt': color_point[i - 1], 'color': 'red'})
                            n_res['retweet_name'].append(
                                [{'name': '预警', 'xAxis': date_list[color_point[i - 1]]}, {'xAxis': date_list[color_point[i]]}])
                        else:
                            n_res['retweet_pieces'].append({'lte': color_point[i], 'gt': color_point[i - 1], 'color': 'green'})
                    n_res['retweet_pieces'].append({'gt': color_point[i], 'color': 'green'})
            else:
                if len(small_check_point)>len(big_check_point):
                    n_res['retweet_pieces'].append({'lte': small_check_point[0], 'color': 'red'})
                    n_res['retweet_name'].append(
                        [{'name': '预警', 'xAxis': date_list[0]}, {'xAxis':  date_list[small_check_point[0]]}])
                    color_point = []
                    color_point.extend(list(chain.from_iterable(zip(small_check_point[:-1], big_check_point))).append(small_check_point[-1]))
                    for i in range(1,len(color_point)):
                        if i%2==1:
                            n_res['retweet_pieces'].append({'lte': color_point[i],'gt':color_point[i-1], 'color': 'green'})
                        else:
                            n_res['retweet_pieces'].append({'lte': color_point[i],'gt':color_point[i-1], 'color': 'red'})
                            n_res['retweet_name'].append(
                                [{'name': '预警', 'xAxis': date_list[color_point[i - 1]]}, {'xAxis': date_list[color_point[i]]}])
                    n_res['retweet_pieces'].append({'gt':color_point[i], 'color': 'green'})
                else:
                    n_res['retweet_pieces'].append({'lte': small_check_point[0], 'color': 'red'})
                    n_res['retweet_name'].append(
                        [{'name': '预警', 'xAxis': date_list[0]}, {'xAxis': date_list[small_check_point[0]]}])
                    color_point = []
                    color_point.extend(
                        list(chain.from_iterable(zip(small_check_point, big_check_point))))
                    for i in range(1, len(color_point)):
                        if i % 2 == 1:
                            n_res['retweet_pieces'].append({'lte': color_point[i], 'gt': color_point[i - 1], 'color': 'green'})
                        else:
                            n_res['retweet_pieces'].append({'lte': color_point[i], 'gt': color_point[i - 1], 'color': 'red'})
                            n_res['retweet_name'].append(
                                [{'name': '预警', 'xAxis': date_list[color_point[i - 1]]}, {'xAxis': date_list[color_point[i]]}])
                    n_res['retweet_pieces'].append({'gt': color_point[i], 'color': 'red'})
                    n_res['retweet_name'].append(
                        [{'name': '预警', 'xAxis': date_list[color_point[i]]}, {'xAxis': date_list[len(n_res['date']) - 1]}])

        #
        #
        #
        # n_res['comment_name'] = []
        # n_res['comment_pieces'] = []
        # change_point = []
        # for i in range(len(n_res['date'])):
        #     if n_res['comment_count'][i] != '-':
        #         if n_res['comment_count'][i] > 1000:
        #             change_point.append(1)
        #         else:
        #             change_point.append(0)
        #     else:
        #         if n_res['comment_count_pred'][i] > 1000:
        #             change_point.append(1)
        #         else:
        #             change_point.append(0)
        # big_check_point = []
        # small_check_point = []
        # date_list = n_res['date']
        # for i in range(1, len(n_res['date'])):
        #     if change_point[i] > change_point[i - 1]:
        #         big_check_point.append(i)
        #     elif change_point[i] < change_point[i - 1]:
        #         small_check_point.append(i)
        #
        # if len(big_check_point) == 0:
        #     if len(small_check_point) == 0:
        #         if n_res['comment_count'][0] > 1000:
        #             n_res['comment_pieces'].append(
        #                 {'lte': len(date_list) - 1, 'gt': 0, 'color': 'red'})
        #             n_res['comment_name'].append(
        #                 [{'name': '预警', 'xAxis': date_list[0]}, {'xAxis': date_list[len(date_list) - 1]}])
        #         else:
        #             n_res['comment_pieces'].append(
        #                 {'lte': len(date_list) - 1, 'gt': 0, 'color': 'blue'})
        #     else:
        #         n_res['comment_pieces'].append(
        #             {'lte': small_check_point[0], 'gt': 0, 'color': 'red'})
        #         n_res['comment_pieces'].append({'lte':  len(date_list) - 1, 'gt': small_check_point[0], 'color': 'blue'})
        #         n_res['comment_name'].append(
        #             [{'name': '预警', 'xAxis': date_list[0]}, {'xAxis': date_list[small_check_point[0]]}])
        #
        # if len(big_check_point) != 0:
        #     if len(small_check_point) == 0:
        #         n_res['comment_pieces'].append(
        #             {'lte': big_check_point[0], 'gt': 0, 'color': 'blue'})
        #         n_res['comment_pieces'].append({'lte':  len(date_list) - 1, 'gt': big_check_point[0], 'color': 'red'})
        #         n_res['comment_name'].append(
        #             [{'name': '预警', 'xAxis': date_list[big_check_point[0]]}, {'xAxis': date_list[-1]}])
        # if len(big_check_point) != 0 and len(small_check_point) != 0:
        #     if big_check_point[0] < small_check_point[0]:
        #         if len(big_check_point) > len(small_check_point):
        #             n_res['comment_pieces'].append({'lte': big_check_point[0], 'color': 'blue'})
        #             color_point = []
        #             color_point.extend(
        #                 list(chain.from_iterable(zip(big_check_point[:-1], small_check_point))).append(
        #                     big_check_point[-1]))
        #             for i in range(1, len(color_point)):
        #                 if i % 2 == 1:
        #                     n_res['comment_pieces'].append(
        #                         {'lte': color_point[i], 'gt': color_point[i - 1],
        #                          'color': 'red'})
        #                     n_res['comment_name'].append([{'name': '预警', 'xAxis': date_list[color_point[i - 1]]},
        #                                                   {'xAxis': date_list[color_point[i]]}])
        #                 else:
        #                     n_res['comment_pieces'].append(
        #                         {'lte': color_point[i], 'gt': color_point[i - 1],
        #                          'color': 'blue'})
        #             n_res['comment_pieces'].append({'gt': color_point[i], 'color': 'red'})
        #             n_res['comment_name'].append([{'name': '预警', 'xAxis': date_list[color_point[i]]},
        #                                           {'xAxis': date_list[len(n_res['date']) - 1]}])
        #         else:
        #             n_res['comment_pieces'].append({'lte': date_list[big_check_point[0]], 'color': 'blue'})
        #             color_point = []
        #             color_point.extend(
        #                 list(chain.from_iterable(zip(big_check_point, small_check_point))))
        #             for i in range(1, len(color_point)):
        #                 if i % 2 == 1:
        #                     n_res['comment_pieces'].append(
        #                         {'lte': color_point[i], 'gt': color_point[i - 1],
        #                          'color': 'red'})
        #                     n_res['comment_name'].append(
        #                         [{'name': '预警', 'xAxis': date_list[color_point[i - 1]]},
        #                          {'xAxis': date_list[color_point[i]]}])
        #                 else:
        #                     n_res['comment_pieces'].append(
        #                         {'lte': color_point[i], 'gt': color_point[i - 1],
        #                          'color': 'blue'})
        #             n_res['comment_pieces'].append({'gt': color_point[i], 'color': 'blue'})
        #     else:
        #         if len(small_check_point) > len(big_check_point):
        #             n_res['comment_pieces'].append({'lte': small_check_point[0], 'color': 'red'})
        #             n_res['comment_name'].append(
        #                 [{'name': '预警', 'xAxis': date_list[0]}, {'xAxis': date_list[small_check_point[0]]}])
        #             color_point = []
        #             color_point.extend(
        #                 list(chain.from_iterable(zip(small_check_point[:-1], big_check_point))).append(
        #                     small_check_point[-1]))
        #             for i in range(1, len(color_point)):
        #                 if i % 2 == 1:
        #                     n_res['comment_pieces'].append(
        #                         {'lte': color_point[i], 'gt': color_point[i - 1],
        #                          'color': 'blue'})
        #                 else:
        #                     n_res['comment_pieces'].append(
        #                         {'lte': color_point[i], 'gt': color_point[i - 1],
        #                          'color': 'red'})
        #                     n_res['comment_name'].append(
        #                         [{'name': '预警', 'xAxis': date_list[color_point[i - 1]]},
        #                          {'xAxis': date_list[color_point[i]]}])
        #             n_res['comment_pieces'].append({'gt': color_point[i], 'color': 'blue'})
        #         else:
        #             n_res['comment_pieces'].append({'lte': small_check_point[0], 'color': 'red'})
        #             n_res['comment_name'].append(
        #                 [{'name': '预警', 'xAxis': date_list[0]}, {'xAxis': date_list[small_check_point[0]]}])
        #             color_point = []
        #             color_point.extend(
        #                 list(chain.from_iterable(zip(small_check_point, big_check_point))))
        #             for i in range(1, len(color_point)):
        #                 if i % 2 == 1:
        #                     n_res['comment_pieces'].append(
        #                         {'lte': date_list[color_point[i]], 'gt': date_list[color_point[i - 1]],
        #                          'color': 'blue'})
        #                 else:
        #                     n_res['comment_pieces'].append(
        #                         {'lte': color_point[i], 'gt': color_point[i - 1],
        #                          'color': 'red'})
        #                     n_res['comment_name'].append(
        #                         [{'name': '预警', 'xAxis': date_list[color_point[i - 1]]},
        #                          {'xAxis': date_list[color_point[i]]}])
        #             n_res['comment_pieces'].append({'gt': color_point[i], 'color': 'red'})
        #             n_res['comment_name'].append(
        #                 [{'name': '预警', 'xAxis': date_list[color_point[i]]},
        #                  {'xAxis': date_list[len(n_res['date']) - 1]}])
        #
        # if len(n_res['comment_name'])==0:
        #     n_res['comment_name'].append([{'name': '', 'xAxis': ''},
        #                  {'xAxis': ''}])
        # if len(n_res['retweet_name'])==0:
        #     n_res['retweet_name'].append([{'name': '', 'xAxis': ''},
        #                  {'xAxis': ''}])
        return JsonResponse(n_res)
