
from django.urls import path, include

from . import callApi

urlpatterns = [
    path('getBotInfo', callApi.getBotInfo, name='getBotInfo'),
    path('sendMessage', callApi.sendMessage, name='sendMessage')
]
