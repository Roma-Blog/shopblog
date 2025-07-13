from django.urls import path
from .views import robots

urlpatterns = [
    path('robots.txt', robots, name='robots'),
]