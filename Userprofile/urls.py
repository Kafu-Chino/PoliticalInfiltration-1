# -*- coding: utf-8 -*-
from django.urls import path
from . import views


urlpatterns = [
    path('test/', views.Test.as_view()),
    path('basic_info/', views.BasicInfo.as_view()),
    path('user_behavior/', views.User_Behavior.as_view()),
    path('user_activity/', views.User_Activity.as_view()),
    path('association/', views.Association.as_view()),
    path('user_topic/', views.Show_topic.as_view()),
    path('user_contact/', views.Show_contact.as_view()),
]
