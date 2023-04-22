from django.contrib import admin
from django.urls import path
from .views import register, login_user, home

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login_user'),
    path('', home, name='home')
]