
from django.urls import path
from . import views

urlpatterns = [
    path('trend/',views.Event_trend.as_view()),
    path('representative/',views.representative_info.as_view()),
    path('person/',views.Person_show.as_view()),
    path('eventshow/',views.Show_event.as_view()),
    path('event_show_sort/', views.Show_event_sort.as_view()),
    path('event_search_sort/', views.search_event_sort.as_view()),
    path('eventadd/',views.Add_event.as_view()),
    path('delete_event/',views.delete_event.as_view()),
    path('einfoshow/',views.Show_event_info.as_view()),
    path('esearch/',views.search_event.as_view()),
    path('show_cal_event/',views.show_cal_event.as_view()),
    path('delete_cal_event/',views.delete_cal_event.as_view()),
    path('related_info/',views.related_info.as_view()),
    path('related_figure/',views.related_figure.as_view()),
    path('geo_out/',views.event_geo_out.as_view()),
    path('geo_in/',views.event_geo_in.as_view()),
    path('info_geo_out/',views.info_geo_out.as_view()),
    path('info_geo_in/',views.info_geo_in.as_view()),
    path('geo_info/',views.geo_info.as_view()),
    path('event_group/',views.Event_Group.as_view()),
    path('timeline/',views.semantic_tl.as_view()),
    path('event_topic/',views.semantic_topic.as_view()),
    path('semantic_info/',views.semantic_info.as_view()),
    path('first_trend/',views.first_info_trend.as_view()),
    path('first_senword/',views.first_sensitive.as_view()),
    path('first_figure/',views.first_figure.as_view()),
    path('first_geo/',views.first_info_geo.as_view()),
    path('first_info/',views.first_info.as_view()),
    path('first_event/',views.first_event.as_view()),
    path('group_create/',views.create_time.as_view()),
    path('group_age/',views.age.as_view()),
    # path('group_geo/',views.group_geo.as_view()),
    path('group_funs/',views.funs_num.as_view()),
    path('group_friends/',views.friends_num.as_view()),
]