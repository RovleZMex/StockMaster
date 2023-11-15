from django.urls import path
from . import views

urlpatterns = [
    path('salidas/', views.OutputHistory, name="outputHistory"),  # Different path for the outputHistory view
    path('entradas/', views.InputHistory, name="inputHistory"),  # Different path for the inputHistory view
    path('editarSalida/<int:orderid>/', views.ModifyOutputOrders, name="outputEdit"),
    path('eliminar-orden/', views.deleteOrderOutput, name="deleteOrderOutput"),
    path('detalles-orden-salida/<int:orderid>/', views.outputDetails, name="outputDetails"),  # path to go to order details
    path('detalles-orden-entrada/<int:orderid>', views.inputOrderDetails, name="inputDetails"),
    path('editar-orden-entrada/<int:orderid>', views.inputOrderEdit, name="inputOrderEdit"),
    path('eliminar-orden/', views.deleteOrder, name="deleteOrder"),
]
