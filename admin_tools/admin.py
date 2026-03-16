# This file is for registering different models in the Admin Page
# Each model that will be registered, will be added as a Managable Model to the Admin Page
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import Field
from admin_tools.models import *


@admin.register(Addon)
class AddonAdmin(ModelAdmin):
    # Display all the fields of Lockable resources
    list_display = [
        str(field).split(".")[-1]
        for field in Addon._meta.get_fields()
        if isinstance(field, Field)
    ]


# Override ResourceExpiryPolicy admin to use autocomplete for lockable_resource field
# This must run after expiry_addon's admin.py, so we import it first
try:
    import expiry_addon.admin  # Ensure expiry_addon's admin is loaded first
    from expiry_addon.models import ResourceExpiryPolicy

    if admin.site.is_registered(ResourceExpiryPolicy):
        # Unregister the default admin
        admin.site.unregister(ResourceExpiryPolicy)

        # Register our custom admin with autocomplete
        class ResourceExpiryPolicyAdmin(ModelAdmin):
            list_display = [
                str(field).split(".")[-1]
                for field in ResourceExpiryPolicy._meta.get_fields()
            ]
            readonly_fields = ["is_expired"]
            # Use autocomplete for lockable_resource - provides search-as-you-type
            autocomplete_fields = ["lockable_resource"]

            list_display.extend(readonly_fields)

        admin.site.register(ResourceExpiryPolicy, ResourceExpiryPolicyAdmin)
except (ImportError, RuntimeError):
    # expiry_addon not installed or not in INSTALLED_APPS, skip
    pass
