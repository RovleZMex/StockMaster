from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('confirm_order/', views.confirm_order, name='confirm_order'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('verify_employee/', views.verify_employee, name='verify_employee'),
    path('logout/', views.logout_worker, name='logout_worker'),
    path('historial-ordenes/', views.order_history, name='workerOrderHistory'),
]

