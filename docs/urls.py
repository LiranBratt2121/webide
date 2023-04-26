from django.urls import path
from . import views

urlpatterns = [
    path('ide/', views.ide),
    path('<slug:slug>/', views.project_ide, name='project_ide'),
    path('create/', views.create_project),
    path('views_projects', views.view_projects)
]
