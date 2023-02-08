from django.contrib import admin
from django.urls import path, include
from . import nwad

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('auth/', include('AUTH.urls')),
    path('api/', include('API.urls')),

    path('', nwad.apiBotList, name=""),
    path('apiBotList', nwad.apiBotList, name="apiBotList"),
    path('login', nwad.login, name="login"),
    path('logout', nwad.logout, name="logout"),
    path('loginFind', nwad.loginFind, name="loginFind"),
    path('join', nwad.join, name="join"),
    path('joinIdCheck', nwad.joinIdCheck, name="joinIdCheck"),

    path('apiList', nwad.apiList, name="apiList"),
    path('api/apiReg', nwad.apiReg, name="api/apiReg"),
    path('api/apiRm', nwad.apiRm, name="api/apiRm"),
    path('api/apiUpd', nwad.apiUpd, name="api/apiUpd"),
    path('api/getApiList', nwad.getApiList, name="api/getApiList"),
    path('api/getApi', nwad.getApi, name="api/getApi"),

    path('botList', nwad.botList, name="botList"),
    path('bot/botReg', nwad.botReg, name="bot/botReg"),
    path('bot/botRm', nwad.botRm, name="bot/botRm"),
    path('bot/botUpd', nwad.botUpd, name="bot/botUpd"),
    path('bot/getBotList', nwad.getBotList, name="api/getBotList"),
    path('bot/getBot', nwad.getBot, name="api/getBot"),

    path('Message/textMessage', nwad.textMessage, name="Message/textMessage"),

    path('Scenario/scenarioReg', nwad.scenarioReg, name="Scenario/scenarioReg"),
    path('botResponse', nwad.botResponse, name="botResponse"),
    path('callback', nwad.callback, name="callback"),
]
