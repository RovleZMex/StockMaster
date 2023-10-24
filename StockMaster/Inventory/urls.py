from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.inventory, name="inventory"),
]