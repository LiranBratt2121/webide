from django.urls import path
from . import views
from django.urls import re_path
from . import consumers

urlpatterns = [
    path('ide/', views.ide),
    path('<slug:slug>/', views.project_ide, name='project_ide'),
    path('create/', views.create_project),
    path('views_projects', views.view_projects)
]

websocket_urlpatterns = [
    re_path(r'ws/<str:project_name>/', consumers.ChatConsumer.as_asgi())
]

urlpatterns += websocket_urlpatterns