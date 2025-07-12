from django.urls import path
from .views import webhook_tg

urlpatterns = [
    path('webhook-tg/', webhook_tg, name='webhook'),
]