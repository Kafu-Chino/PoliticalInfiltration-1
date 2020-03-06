"""PoliticalInfiltration URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_swagger.views import get_swagger_view
from rest_framework import permissions


urlpatterns = [
    path('admin/', admin.site.urls),
    path('Mainevent/', include('Mainevent.urls')),
    path('Userprofile/', include('Userprofile.urls')),
    path('Usermanager/', include('Usermanager.urls')),
    path('Informationspread/', include('Informationspread.urls')),
    path('Systemmanage/', include('Systemmanage.urls')),
    path(r'docs/', get_swagger_view(title='ApiDocs')),
]
