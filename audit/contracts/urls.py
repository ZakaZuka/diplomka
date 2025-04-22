# # contracts/urls.py
# from django.urls import path
# from .views import upload_contract

# urlpatterns = [
#     path('', upload_contract, name='upload_contract'),
# ]

from django.urls import path
from .views import contract_analysis_view

urlpatterns = [
    path('', contract_analysis_view, name='analyze_contract'),
]
