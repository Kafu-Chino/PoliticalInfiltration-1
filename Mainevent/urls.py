
from django.urls import path
from . import views,datain,show_task


urlpatterns = [
    path('test/', views.Test.as_view()),
    path('add/',datain.add_by_input),
    path('push/',datain.add_from_push),
    path('show/',show_task.show),
]
