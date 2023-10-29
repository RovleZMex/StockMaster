from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('inventario/', include("Inventory.urls"), name="inventory"),
    path('historial/', include("OutputHistory.urls"), name="history"),
    path('personal/', views.workers, name="workers"),
    path('iniciar-sesion/', views.LoginPage, name="login"),
    path('cerrar-sesion/', views.LogoutPage, name="logout"),
]
