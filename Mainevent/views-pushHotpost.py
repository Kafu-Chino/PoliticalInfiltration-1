# -- coding:utf-8 --
from django.shortcuts import render
from django.db import models

from Mainevent.models import Hot_post


def push(request):
    # 页面响应,从数据库取热帖展示
    hot_post_display = Hot_post.objects.all().values_list()  # 取出所有列，并生成一个列表
    return render(request, 'hot_post.html', {'Hot_post': hot_post_display})
