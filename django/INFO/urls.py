from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.login, name="login"),
    path('list/', views.list, name="list"),
    path('Insert_into_table/', views.Insert_into_table, name='Insert_into_table'),
    path('login_view/', views.login_view, name="login_view"),
    path('list2/', views.list2, name="list2"),
]
