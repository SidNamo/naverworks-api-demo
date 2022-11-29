
from django.urls import path, include
from . import authApi

urlpatterns = [
    path('jwt', authApi.authJwt, name='jwt')
]
