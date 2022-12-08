
from django.urls import path, include

from . import callApi

urlpatterns = [
    path('getBotInfo', callApi.getBotInfo, name='getBotInfo'),
    path('sendMessage', callApi.sendMessage, name='sendMessage'),
    path('createChannel', callApi.createChannel, name='createChannel'),
    path('getUserInfo', callApi.getUserInfo, name='getUserInfo'),
    path('getChannelMembers', callApi.getChannelMembers, name='getChannelMembers'),
]
