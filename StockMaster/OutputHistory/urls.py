from django.urls import path

from . import views

urlpatterns = [
    path('salidas/', views.outputHistory, name="outputHistory"),  # Different path for the outputHistory view
    path('entradas/', views.inputHistory, name="inputHistory"),  # Different path for the inputHistory view
]
