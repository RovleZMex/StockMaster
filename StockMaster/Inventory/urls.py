from django.urls import path

from . import views

urlpatterns = [
    path('', views.Inventory, name="inventory"),
    path('añadir-productos/', views.AddProducts, name="addProducts"),
    path('filter/', views.FilterInventory, name="filtered"),
    path('editar/<int:productid>/', views.EditProduct, name="editProduct"),
    path('add-product/', views.AddProduct, name="add_product"),
    path('register-buy-order', views.HandleProductData, name="registerBuyOrder"),
    path('informe-producto/<int:productid>', views.ProductGraph, name="productGraph"),
    path('gpmd/', views.GetProductQuantityData, name='productMonthData'),
    path('gppd/', views.GetProductPriceData, name='productDataPrice'),
    path('detalles-producto/<int:productid>', views.ProductDetails, name="productDetails"),
]
