from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('auth/nonce/', views.get_nonce, name='get_nonce'),  # Важно: без параметра в URL
    path('auth/metamask/', views.metamask_login_view, name='metamask_login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/nonce/<str:address>/', views.get_nonce, name='get_nonce'),
]
