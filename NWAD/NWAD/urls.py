from django.contrib import admin
from django.urls import path, include
from . import nwad

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('auth/', include('AUTH.urls')),
    path('api/', include('API.urls')),

    path('', nwad.index, name="main"),
    path('login', nwad.login, name="login"),
    path('logout', nwad.logout, name="logout"),
    path('loginFind', nwad.loginFind, name="loginFind"),
    path('join', nwad.join, name="join"),
    path('joinIdCheck', nwad.joinIdCheck, name="joinIdCheck"),

    path('apiList', nwad.apiList, name="apiList"),
    path('api/apiReg', nwad.apiReg, name="api/apiReg"),
    path('api/apiRm', nwad.apiRm, name="api/apiRm"),
    path('api/getApiList', nwad.getApiList, name="api/getApiList"),

    path('botList', nwad.botList, name="botList"),
    path('bot/botReg', nwad.botReg, name="bot/botReg"),
    path('bot/botRm', nwad.botRm, name="api/botRm"),
    path('bot/getBotList', nwad.getBotList, name="api/getBotList"),

    path('Message/textMessage', nwad.textMessage, name="Message/textMessage"),

    path('Scenario/scenarioReg', nwad.scenarioReg, name="Scenario/scenarioReg"),
    path('botResponse', nwad.botResponse, name="botResponse"),
    path('callback', nwad.callback, name="callback"),
]
