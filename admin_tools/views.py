import os
from django.shortcuts import render, redirect, reverse
from lockable_resource.models import LockableResource
from django.contrib import messages
from admin_tools.models import Addon
from rlocker import settings
import yaml


# The index.
def index(request):
    # For every administrative tool, add this to the tools list to visualize it
    # Manage the list of tools from here
    # Supported k&v are:
    # - name :str
    # - url :reverse obj
    tools = [
        {
            "name": "Import Lockable Resources From YAML",
            "url": reverse("admin_tools:import_lockable_resources_from_yaml"),
        },
        {
            "name": "Plugin Management",
            "url": reverse("admin_tools:manage_plugins"),
        },

    ]
    return render(
        request,
        template_name="admin_tools/index.html",
        context={
            "enum_tools": enumerate(tools, start=1)
        },
    )


def import_lockable_resources_from_yaml(request):
    if request.method == "GET":
        return render(request, template_name="admin_tools/import_yaml.html")

    if request.method == "POST":
        yaml_text = request.POST.get("lockable_resources_yaml")
        parsed_yaml = yaml.safe_load(yaml_text)
        for lr in parsed_yaml["lockable_resources"]:
            lr_name = lr.get("name")
            lr_exists = len(LockableResource.objects.filter(name=lr_name)) > 0
            if lr_exists:
                lr_obj = LockableResource.objects.get(name=lr_name)
                for attribute, value in lr.items():
                    setattr(lr_obj, attribute, value)
                lr_obj.save()
            else:
                new_lr_obj = LockableResource(**lr)
                new_lr_obj.save()

        messages.success(
            request,
            message=f"Import of YAML completed successfully!",
        )
        return redirect("admin_tools:import_lockable_resources_from_yaml")

def manage_plugins(request):
    addons = Addon.objects.all()
    if request.method == "GET":
        return render(
            request,
            template_name="admin_tools/manage_addons.html",
            context={
                "addons" : addons
            }
        )
    if request.method == "POST":
        addon_application_name = request.POST.get("addon_application_name")
        addon_obj = Addon.objects.get(addon_application_name)
        addon_obj.is_installed = True
        addon_obj.save()
        return redirect("admin_tools:manage_plugins")
