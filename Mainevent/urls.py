<<<<<<< HEAD
from django.urls import path
from . import views


urlpatterns = [
    path('test/', views.Test.as_view()),

<<<<<<< HEAD
]
=======
from django.urls import path
from . import views,datain,show_task


urlpatterns = [
    path('test/', views.Test.as_view()),
    path('add/',datain.add_by_input),
    path('push/',datain.add_from_push),
    path('show/',show_task.show),
=======
>>>>>>> 1fbf181343fdeacfa4aaef5f2c9e91721f481a1b
]
>>>>>>> nimengli:url configuration
