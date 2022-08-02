from django.urls import path
from patch_notifier import views

app_name = "patch_notifier"

urlpatterns = [
    path("update_first_visit/", views.update_first_visit, name="update_first_visit"),
]
