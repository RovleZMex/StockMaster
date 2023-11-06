from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.inventory, name="inventory"),
    path('añadir-productos/', views.AddProducts, name="addProducts"),
    path('filter/', views.filterInventory, name="filtered"),
    path('editar/<int:productid>/', views.EditProduct, name="editProduct"),
    path('add-product/', views.add_product, name="add_product"),
    path('register-buy-order', views.handle_product_data, name="registerBuyOrder")
]
