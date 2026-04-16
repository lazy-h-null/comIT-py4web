from django.contrib import admin
from django.urls import path
from static_pages_1 import views

urlpatterns = [
    path('', views.home, name="home"),
    path('contact/', views.contact, name="contact")
]
