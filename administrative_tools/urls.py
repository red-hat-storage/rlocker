from django.urls import path

from administrative_tools import views

# In order to call to those as `administrative_tools:view_name` we need this
app_name='administrative_tools'

urlpatterns = [
    path('export_lockable_resources/', views.import_lockable_resources, name='import_lockable_resources'),
    path('', views.index, name='index'),
]
