"""rest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers, serializers, viewsets
from django.urls import path

from devices import views
from devices.models import Alerts


urlpatterns = [
    url(r'^$', views.device_list.as_view()),
    url(r'^detail$', views.device_detail.as_view()),
    url(r'^alerts$',views.alerts_list.as_view()),
    url(r'^alert$',views.device_alerts.as_view()),
    url(r'^networkList$',views.networkList_list.as_view()),
    url(r'^networks$',views.device_network.as_view()),
    url(r'^upload/(?P<filename>[^/]*)$', views.device_upload.as_view()),
    url(r'^stream$',views.device_stream.as_view()),
    url(r'^events$',views.device_eventQ.as_view()),
    url(r'^event$',views.device_event.as_view()),
    url(r'^statistic$',views.device_statistic.as_view()),
    url(r'^location$',views.device_location.as_view()),
    url(r'^statistics$',views.device_statistic_list.as_view()),
    url(r'^locations$',views.device_location_list.as_view()),
]
