# -*- coding: utf-8 -*-
from django.urls import path
from . import views


urlpatterns = [
    path('test/', views.Test.as_view()),
    path('show_info/', views.Show_Info.as_view()),
]
