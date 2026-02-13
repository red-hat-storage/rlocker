# This file is for registering different models in the Admin Page
# Each model that will be registered, will be added as a Managable Model to the Admin Page
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import Field
from lockable_resource.models import *


@admin.register(LockableResource)
class LockableResourceAdmin(ModelAdmin):
    # Display all the fields of Lockable resources
    list_display = [
        str(field).split(".")[-1]
        for field in LockableResource._meta.get_fields()
        if isinstance(field, Field)
    ]

    # Add filters for easier resource management
    list_filter = ["in_maintenance", "is_locked", "provider"]

    # Add search capability
    search_fields = ["name", "provider", "labels_string", "signoff"]

    # Register admin actions
    actions = ["enter_maintenance_mode", "exit_maintenance_mode"]

    @admin.action(description="Move selected resources to maintenance mode")
    def enter_maintenance_mode(self, request, queryset):
        """
        Admin action to move selected resources into maintenance mode.
        Updates all selected resources and sets in_maintenance=True.
        """
        updated_count = queryset.update(in_maintenance=True)
        self.message_user(
            request,
            f"{updated_count} resource(s) successfully moved to maintenance mode.",
            level="SUCCESS",
        )

    @admin.action(description="Exit selected resources from maintenance mode")
    def exit_maintenance_mode(self, request, queryset):
        """
        Admin action to remove selected resources from maintenance mode.
        Updates all selected resources and sets in_maintenance=False.
        """
        updated_count = queryset.update(in_maintenance=False)
        self.message_user(
            request,
            f"{updated_count} resource(s) successfully exited from maintenance mode.",
            level="SUCCESS",
        )
