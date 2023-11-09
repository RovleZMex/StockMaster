from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path('salidas/', views.outputHistory, name="outputHistory"),  # Different path for the outputHistory view
    path('entradas/', views.inputHistory, name="inputHistory"),  # Different path for the inputHistory view
    path('detallesTrabajador/<int:orderid>/', views.outputDetails, name="outputDetails"),  # path to go to order details
    path('inventario/', views.redirection, name="inventory"),  # path for the redirection view
=======
    path('salidas/', views.OutputHistory, name="outputHistory"),  # Different path for the outputHistory view
    path('entradas/', views.InputHistory, name="inputHistory"),  # Different path for the inputHistory view
>>>>>>> 3eba94c75b21fd678e5be6c1f5388b670a92f0f7
]
