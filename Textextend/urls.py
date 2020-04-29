#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Hu

@time: 2020/2/7 17:46

@file: urls.py
"""

from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.Test.as_view()),
    path('stshow/',views.Show_sensitivetext.as_view()),
    path('stdelete/',views.Delete_sensitivetext.as_view()),
    path('extentsbmit/',views.Submit_extent.as_view()),
    path('seedshow/',views.Show_seedtext.as_view()),
    path('seeddelete/',views.Delete_seedtext.as_view()),
    path('seeddelete/',views.Delete_seedtext.as_view()),

]