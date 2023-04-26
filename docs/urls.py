from django.urls import path
from . import views

urlpatterns = [
    path('ide/', views.ide),
    path('create/', views.create_project)
]




