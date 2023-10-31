from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.inventory, name="inventory"),
    path('añadir-productos/', views.AddProducts, name="addProducts"),
    path('filter/', views.filterInventory, name="filtered"),
    path('editar/<int:productid>/', views.EditProduct, name="editProduct"),
]
