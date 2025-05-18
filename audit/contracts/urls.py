# # contracts/urls.py
# from django.urls import path
# from .views import upload_contract

# urlpatterns = [
#     path('', upload_contract, name='upload_contract'),
# ]

from django.urls import path
from .views import upload_contract

app_name = 'contracts'

urlpatterns = [
    path('upload/', upload_contract, name='upload')
]