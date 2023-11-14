from django.urls import path
from . import views

urlpatterns = [
    path('salidas/', views.OutputHistory, name="outputHistory"),  # Different path for the outputHistory view
    path('entradas/', views.InputHistory, name="inputHistory"),  # Different path for the inputHistory view
    path('detallesTrabajador/<int:orderid>/', views.outputDetails, name="outputDetails"),  # path to go to order details
    path('editarSalida/<int:orderid>/', views.ModifyOutputOrders, name="outputEdit"),
    path('eliminar-orden/', views.deleteOrderOutput, name="deleteOrderOutput"),
]
