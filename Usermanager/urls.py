# -*- coding: utf-8 -*-
from django.urls import path
from . import views


urlpatterns = [
    path('test/', views.Test.as_view()),
    path('user_info/', views.UserInfo.as_view()),
    path('user_login/', views.User_Login.as_view()),
    path('user_logout/', views.User_Logout.as_view()),
    path('user_add/', views.User_Add.as_view()),
    path('user_delete/', views.User_Delete.as_view()),
]