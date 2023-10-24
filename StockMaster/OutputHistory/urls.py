from django.urls import path

from . import views

urlpatterns = [
    path('trabajadores/', views.history, name="outputHistoryWorker"),  # Different path for the history view
    path('salidas/', views.outputHistory, name="outputHistory"),  # Different path for the outputHistory view
    path('entradas/', views.inputHistory, name="inputHistory"),  # Different path for the inputHistory view
]
