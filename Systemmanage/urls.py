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
    path('swshow/',views.Show_sensitive_word.as_view()),
    path('swtshow/',views.Show_sensitive_word_transform.as_view()),
    path('swadd/',views.Add_sensitive_word.as_view()),
    path('swtdelete/',views.Delete_sensitive_word_transform.as_view()),
    path('swpdelete/',views.Delete_sensitive_word_prototype.as_view()),
    path('gparametershow/',views.Show_global_parameter.as_view()),
    path('gparametermodify/',views.Modify_global_parameter.as_view()),
    path('eswadd/',views.Add_sensitiveword().as_view()),
    path('eswdelete/',views.Delete_sensitiveword.as_view()),
    path('stadd/',views.Add_sensitivetext.as_view()),
    path('stdelete/',views.Delete_sensitivetext.as_view()),
    path('kwadd/',views.Add_keyword.as_view()),
    path('kwdelete/',views.Delete_keyword.as_view()),
    path('epadd/',views.Add_eventparameter.as_view()),
    path('epupdate/',views.Update_eventparameter.as_view()),
    path('kwshow/',views.Show_eventkeyword.as_view()),
    path('eswshow/',views.Show_eventsensitiveword.as_view()),
    path('epshow/',views.Show_eventparameter.as_view()),
]