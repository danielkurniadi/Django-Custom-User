from django.contrib import admin
from django.urls import path, include
from .views import duty_handler

urlpatterns = [
    path('api/', duty_handler, name='duty'),
]
