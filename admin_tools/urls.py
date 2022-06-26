from admin_tools import views
from django.urls import path

# In order to call to those as `admin_tools:view_name` we need this
app_name = "admin_tools"

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "import_yaml",
        views.import_lockable_resources_from_yaml,
        name="import_lockable_resources_from_yaml",
    ),
]
