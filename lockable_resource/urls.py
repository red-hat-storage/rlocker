from lockable_resource import views
from django.urls import path

urlpatterns = [
    path("", views.lockable_resources_page, name="lockable_resources_page"),
    path("<slug>/", views.lockable_resource_more_info, name="lockable_resource_more_info"),
]
