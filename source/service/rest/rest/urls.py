"""xcmarket_rest URL Configuration

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
from django.contrib import admin
from django.urls import path
from django.conf.urls import url

from myapp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^hello/(\d+)/(\d+)/$', hello),
    path('get_recommend_currency', get_recommend_currency),
    path('get_scope_percent', get_scope_percent),
    # url(r'^get_increase_list/(\d+)/(\d+)/$', get_increase_list),
    # url(r'^get_descrease_list/(\d+)/(\d+)/$', get_descrease_list),
    # url(r'^get_turn_volume_list/(\d+)/(\d+)/$', get_turn_volume_list),
    url(r'^get_currency_list/([a-z_]+)/(desc|asc)/(\d+)/(\d+)/$', get_currency_list),
    path('get_hot_currency', get_hot_currency),
    url(r'^search_currency/([a-z_\u4E00-\u9FA5A]+)/(\d+)/(\d+)/$', search_currency),
]
