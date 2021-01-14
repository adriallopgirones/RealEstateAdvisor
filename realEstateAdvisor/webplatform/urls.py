from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="webplatform-home"),
    path('cityOverview/', views.cityOverviewView, name="webplatform-cityOverview"),
]

