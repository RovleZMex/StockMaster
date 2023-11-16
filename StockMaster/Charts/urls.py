from django.urls import path

from . import views

urlpatterns = [
    path("", views.ReportCharts, name="reportCharts"),
    path("inventario-textual/", views.TextInventory, name="textInventory"),
    path("gastos-textual/", views.TextExpense, name="textExpense"),
    path('inventario-pdf/', views.ViewPDF.as_view(), name="viewPDF"),
    path("gspm/", views.GetStockMonth, name="getStockMonth"),
    path("gcpm/", views.GetCategoriesMonth, name="getCategoriesMonth"),
    path("gppm/", views.GetPercentagesMonth, name="getPercentagesPerCategory")
]
