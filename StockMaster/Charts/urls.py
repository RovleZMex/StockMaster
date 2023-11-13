from django.urls import path

from . import views

urlpatterns = [
    path("", views.ReportCharts, name="reportCharts"),
    path("gspm/", views.GetStockMonth, name="getStockMonth"),
    path("gcpm/", views.GetCategoriesMonth, name="getCategoriesMonth"),
    path("gppm/", views.GetPercentagesMonth, name="getPercentagesPerCategory")
]
