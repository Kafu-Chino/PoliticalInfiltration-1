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
    path('stadd/',views.Add_sensitivetext.as_view()),
    path('stshow/',views.Show_sensitivetext.as_view()),
    path('stdelete/',views.Delete_sensitivetext.as_view()),
    path('extentsbmit/',views.Submit_extent.as_view()),
    path('seedshow/',views.Show_seedtext.as_view()),
    path('seeddelete/',views.Delete_seedtext.as_view()),
    path('auditsubmit/',views.Add_audittext.as_view()),
    path('auditshow/',views.Show_audittext.as_view()),
    path('auditdelete/',views.Delete_audittext.as_view()),
    path('check/',views.Check.as_view()),
    path('process/', views.Process.as_view()),
]