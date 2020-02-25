
from django.urls import path
from . import views

urlpatterns = [
    path('trend/',views.Event_trend.as_view()),
    path('representative/',views.representative_info.as_view()),
    path('person/',views.Person_show.as_view()),
    path('eventshow/',views.Show_event.as_view()),
    path('eventadd/',views.Add_event.as_view()),
    path('einfoshow/',views.Show_event_info.as_view()),
    path('esearch/',views.search_event.as_view()),
    path('related_info/',views.related_info.as_view()),
    path('related_figure/',views.related_figure.as_view()),
    path('geo_out/',views.event_geo_out.as_view()),
    path('geo_in/',views.event_geo_in.as_view()),
    path('info_geo_out/',views.info_geo_out.as_view()),
    path('info_geo_in/',views.info_geo_in.as_view()),
    path('geo_info/',views.geo_info.as_view()),
    path('event_special/',views.Event_Special.as_view()),
    path('timeline/',views.semantic_tl.as_view()),
    path('event_topic/',views.semantic_topic.as_view()),
    path('semantic_info/',views.semantic_info.as_view()),
]