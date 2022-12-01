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
    path('testLogin', nwad.testLogin, name="testLogin"),
    path('join', nwad.join, name="join"),
    path('apiList', nwad.apiList, name="apiList"),
    path('api/apiReg', nwad.apiReg, name="api/apiReg"),
    path('api/apiRm', nwad.apiRm, name="api/apiRm"),
    path('api/getApiList', nwad.getApiList, name="api/getApiList"),
    path('botList', nwad.botList, name="botList"),
    path('bot/botReg', nwad.botReg, name="bot/botReg"),
    path('bot/botRm', nwad.botRm, name="api/botRm"),
    path('bot/getBotList', nwad.getBotList, name="api/getBotList"),
]
