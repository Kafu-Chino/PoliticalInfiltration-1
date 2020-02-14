# -*- coding: utf-8 -*-
from django.urls import path
from . import views


urlpatterns = [
    path('test/', views.Test.as_view()),
    path('basic_info/', views.BasicInfo.as_view()),
    path('user_behavior/', views.User_Behavior.as_view()),
    path('user_activity/', views.User_Activity.as_view()),
    path('association/', views.Association.as_view()),
    path('user_prefer/', views.Show_prefer.as_view()),
    path('user_contact/', views.Show_contact.as_view()),
    path('user_keyword/', views.Show_keyword.as_view()),
    path('figure_info/', views.Show_figure.as_view()),
    path('figure_create/', views.Figure_create.as_view()),
    path('figure_delete/', views.Figure_delete.as_view()),
    path('figure_search/', views.search_figure.as_view()),
    path('user_sentiment/', views.User_Sentiment.as_view()),
]
