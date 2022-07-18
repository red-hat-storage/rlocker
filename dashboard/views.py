import lockable_resource.constants as l_r_const
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from lockable_resource.models import LockableResource
from lockable_resource.label_manager import LabelManager
from lockable_resource.action_manager import LRActionObjectsHandler
from patch_notifier.models import FirstVisit


def dashboard_page(request):
    if request.method == "GET":
        label_managers = [
            LabelManager(label) for label in LockableResource.get_all_labels()
        ]
        label_managers.sort(key=lambda x: x.label)
        display_patch_notes = (
            len(FirstVisit.objects.filter(user=request.user)) == 0
            if request.user.is_authenticated
            else False
        )

        locked_sorted_lrs = LockableResource.objects.filter(is_locked=True).order_by(
            "locked_time"
        )
        maintenance_lrs = LockableResource.objects.filter(in_maintenance=True)
        unavailable_resources = [lr for lr in locked_sorted_lrs]
        for lr in maintenance_lrs:
            if lr not in unavailable_resources:
                unavailable_resources.append(lr)

        return render(
            request,
            template_name="dashboard/index.html",
            context={
                "label_managers": label_managers,
                "free_resources": LockableResource.objects.filter(
                    is_locked=False, in_maintenance=False
                ),
                "unavailable_resources": unavailable_resources,
                "user_locked_resources": LockableResource.objects.filter(
                    Q(is_locked=True) & Q(signoff__startswith=request.user.username)
                ),
                "display_patch_notes": display_patch_notes,
            },
        )
    if request.method == "POST":
        desired_action_obj = LRActionObjectsHandler(
            request
        ).get_desired_action_instance()
        desired_action_obj.complete_action()

        return redirect("dashboard_page")
