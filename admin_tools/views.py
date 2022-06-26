from django.shortcuts import render, redirect
from lockable_resource.models import LockableResource
from django.contrib import messages
import yaml


# For every administrative tool, add this to the tools list to visualize it in
# The index.
def index(request):
    tools = ["Import Lockable Resources From YAML"]
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
