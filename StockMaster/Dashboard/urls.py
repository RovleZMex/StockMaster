from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('inventario/', include("Inventory.urls"), name="inventory"),
    path('historial/', include("OutputHistory.urls"), name="history"),
]
