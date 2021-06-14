# This file is for registering different models in the Admin Page
# Each model that will be registered, will be added as a Managable Model to the Admin Page
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from lockable_resource.models import *


@admin.register(LockableResource)
class LockableResourceAdmin(ModelAdmin):
    # Display all the fields of Lockable resources
    list_display = [
        str(field).split(".")[-1] for field in LockableResource._meta.get_fields()
    ]
