import os
from django.shortcuts import render, redirect, reverse
from lockable_resource.models import LockableResource
from django.contrib import messages
from admin_tools.models import Addon
import admin_tools.constants as const
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
            "name": "Addon Management",
            "url": reverse("admin_tools:manage_addons"),
        },
    ]
    return render(
        request,
        template_name="admin_tools/index.html",
        context={"enum_tools": enumerate(tools, start=1)},
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


def manage_addons(request):
    addons = Addon.objects.all()
    if request.method == "GET":
        return render(
            request,
            template_name="admin_tools/manage_addons.html",
            context={"addons": addons},
        )
    if request.method == "POST":
        addon_application_name = request.POST.get("addon_application_name")
        action = request.POST.get(
            "action"
        )  # TODO: Maybe extend the class inside lockable_resource/action_manager.py and use it's methods ?

        addon_obj = Addon.objects.get(application_name=addon_application_name)
        # Not using a one-liner if here because more actions might be needed for an addon in the future
        if action == const.ACTION_INSTALL_ADDON:
            addon_obj.is_installed = True
        elif action == const.ACTION_UNINSTALL_ADDON:
            addon_obj.is_installed = False
        addon_obj.save()
        messages.info(
            request,
            f"{addon_application_name} installed/uninstalled! "
            f"A restart of the Resource Locker is required for completing the actions successfully, "
            f"please consider executing python manage.py prepare_installed_addons and then runserver!",
        )
        return redirect("admin_tools:manage_addons")
