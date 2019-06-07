from django.contrib import admin
from django.urls import path, include
from .views import duty_handler, duty_view

urlpatterns = [
    path('', duty_view, name='duty-page'),
    path('api/', duty_handler, name='duty-api'),
]
