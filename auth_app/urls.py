from django.urls import path, include
from rest_framework import routers
from . import views

routers = routers.DefaultRouter()
routers.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(routers.urls)),
    path('login/', views.LoginView.as_view(), name='login'),
]