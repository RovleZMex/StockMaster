from django.urls import path

from . import views

urlpatterns = [
    path("", views.ReportCharts, name="reportCharts"),
    path("gspm/", views.GetStockMonth, name="getStockMonth"),
]
