from django.urls import path
from . import views
from .activity_parsers.strava_parser import exchange_token

urlpatterns = [
    path('', views.index, name='index'),
    path('exchange_token/', exchange_token, name='exchange_token'),
]