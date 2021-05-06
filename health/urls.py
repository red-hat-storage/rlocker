from health import views
from django.urls import path

urlpatterns = [
    path('healthcheck', views.health_check, name='health_check'),
]