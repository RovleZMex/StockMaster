from django.urls import path

from . import views

urlpatterns = [
    path('', views.outputHistory, name="outputHistory"),
    path('login/', views.LoginPage, name="login"),
    path('logout/', views.LogoutPage, name="logout")
]
