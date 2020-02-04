
from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.Test.as_view()),
    #path('add/',views.AddByInput.as_view()),
    #path('push/',views.AddFromPush.as_view()),
    #path('show/',views.Show.as_view()),
    path('Hotpost/',views.push_Hotpost.as_view()),
    path('person/',views.Person_show.as_view()),
    path('taskshow/',views.Show_task.as_view()),
    path('eventshow/',views.Show_event.as_view()),
    path('einfoshow/',views.Show_event_info.as_view()),
    path('esearch/',views.search_event.as_view()),
    path('createt/',views.Task_create.as_view()),
    path('deletet/',views.Task_delete.as_view()),
    path('related/',views.figure_info.as_view()),
    path('seninfo/',views.Sen_info.as_view()),
]