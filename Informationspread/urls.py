# -*- coding: utf-8 -*-
from django.urls import path
from . import views


urlpatterns = [
    path('show_info/', views.Show_Info.as_view()),
    path('seninfo/',views.Sen_info.as_view()),
]
