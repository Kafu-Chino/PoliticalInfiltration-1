
from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.Test.as_view()),
    path('add/',views.AddByInput.as_view()),
    path('push/',views.AddFromPush.as_view()),
    path('show/',views.Show.as_view()),
]
# >>>>>>> nimengli:url configuration
