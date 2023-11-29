from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.login, name="login"),
    path('list/', views.list, name="list"),
    path('test/', views.test, name="test"), #추가
    path('Insert_into_table/', views.Insert_into_table, name='Insert_into_table'),
]
