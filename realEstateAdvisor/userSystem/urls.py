from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.register, name="userSystem-register"),
    path('login/', auth_views.LoginView.as_view(template_name='userSystem/login.html'), name='userSystem-login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='userSystem/logout.html'), name='userSystem-logout')
]