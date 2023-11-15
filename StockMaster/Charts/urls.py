from django.urls import path

from . import views

urlpatterns = [
    path("inventario-graficas/", views.ReportCharts, name="reportCharts"),
    path("inventario-textual/", views.TextInventory, name="textInventory"),
    path("gastos-graficas/", views.ExpensesCharts, name="expensesCharts"),
    path('inventario-pdf/', views.ViewPDF.as_view(), name="viewPDF"),
    path("gspm/", views.GetStockMonth, name="getStockMonth"),
    path("gcpm/", views.GetCategoriesMonth, name="getCategoriesMonth"),
    path("gppm/", views.GetPercentagesMonth, name="getPercentagesPerCategory"),
    path("gepm/", views.GetExpensesMonth, name="getExpensesMonth"),
    path("gepcm/", views.GetExpensesPerCategoryMonth, name="getExpensesPerCategory"),
    path("geppm/", views.GetExpensesPercentages, name="getExpensesPercentages")
]
