
from django.urls import path
from . import views

urlpatterns = [
    path('trend/',views.Event_trend.as_view()),
    path('representative/',views.representative_info.as_view()),
    path('person/',views.Person_show.as_view()),
    path('eventshow/',views.Show_event.as_view()),
    path('einfoshow/',views.Show_event_info.as_view()),
    path('esearch/',views.search_event.as_view()),
    path('related/',views.figure_info.as_view()),
]