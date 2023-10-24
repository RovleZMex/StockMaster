from django.urls import path
from . import views

urlpatterns = [
    path('outputHistoryWorker/', views.history, name="outputHistoryWorker"),  # Different path for the history view
    path('outputHistory/', views.outputHistory, name="outputHistory"),  # Different path for the outputHistory view
    path('inputHistory/', views.inputHistory, name="inputHistory"),  # Different path for the inputHistory view
]
