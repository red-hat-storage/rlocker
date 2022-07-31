from admin_tools import views, run_startup
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
    path(
        "manage_plugins",
        views.manage_plugins,
        name="manage_plugins",
    ),
]


# Use this section to call to a code that runs one time once the application loads:
run_startup.main()
