# -*- coding: utf-8 -*-
from django.urls import path
from . import views


urlpatterns = [
    # path('test/', views.Test.as_view()),
    path('figure_info/', views.show_figure_info.as_view()),
    path('user_behavior/', views.User_Behavior.as_view()),
    path('user_activity/', views.User_Activity.as_view()),
    path('association/', views.Association.as_view()),
    path('user_topic/', views.Show_topic.as_view()),
    path('user_contact/', views.Show_contact.as_view()),
    path('user_keyword/', views.Show_keyword.as_view()),
    path('figure_show/', views.Show_figure.as_view()),
    path('figure_create/', views.Figure_create.as_view()),
    path('figure_delete/', views.Figure_delete.as_view()),
    path('figure_search/', views.search_figure.as_view()),
    path('related_info/', views.related_info.as_view()),
    path('related_event/', views.related_event.as_view()),
    path('user_sentiment/', views.User_Sentiment.as_view()),
    path('user_influence/', views.User_Influence.as_view()),
]
