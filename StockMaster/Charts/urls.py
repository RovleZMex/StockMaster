from django.urls import path
from . import views

urlpatterns = [
    path("", views.inventory_category_chart, name="inventory_category_chart")
]