# -*- coding: utf-8 -*-
from django.urls import path
from . import views


urlpatterns = [
    path('show_info/', views.Show_Info.as_view()),
    path('trend/',views.Trend.as_view()),
    path('infopred/',views.Info_spread.as_view()),
]
