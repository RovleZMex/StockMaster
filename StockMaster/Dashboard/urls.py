from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.Dashboard, name="dashboard"),
    path('inventario/', include("Inventory.urls"), name="inventory"),
    path('historial/', include("OutputHistory.urls"), name="history"),
    path('personal/', views.Workers, name="workers"),
    path('iniciar-sesion/', views.LoginPage, name="login"),
    path('cerrar-sesion/', views.LogoutPage, name="logout"),
]
