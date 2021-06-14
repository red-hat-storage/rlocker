from dashboard import views
from django.urls import path

urlpatterns = [
    path("", views.dashboard_page, name="dashboard_page"),
    path("dashboard/", views.dashboard_page, name="dashboard_page"),
]
