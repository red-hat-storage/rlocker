from django.contrib import admin
from .models import ResouceHW
# function is used to register a model with the Django admin site. 
# This registration allows you to manage instances of the model through the Django admin interface.
admin.site.register(ResouceHW)
