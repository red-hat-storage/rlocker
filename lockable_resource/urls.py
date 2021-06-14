from lockable_resource import views
from django.urls import path

urlpatterns = [path("", views.lockable_resources_page, name="lockable_resources_page")]
