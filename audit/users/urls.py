from django.urls import path
from . import views
from django.shortcuts import render

app_name = 'users'

urlpatterns = [
    path('nonce/', views.get_nonce, name='get_nonce'),
    path('login/', views.verify_login, name='verify_login'),
    path('profile/', lambda request: render(request, 'users/profile.html'), name='profile'),
]
