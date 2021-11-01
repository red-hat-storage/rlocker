import lockable_resource.constants as l_r_const
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from lockable_resource.models import LockableResource
from rqueue.models import Rqueue
from lockable_resource.label_manager import LabelManager
from patch_notifier.models import FirstVisit


def dashboard_page(request):
    if request.method == 'GET':
        label_managers = [
            LabelManager(label) for label in LockableResource.get_all_labels()
        ]
        label_managers.sort(key=lambda x: x.label)
        display_patch_notes = len(FirstVisit.objects.filter(user=request.user)) == 0 if request.user.is_authenticated else False
        return render(
            request,
            template_name="dashboard/index.html",
            context={
                "label_managers": label_managers,
                "free_resources": LockableResource.objects.filter(
                    is_locked=False, in_maintenance=False
                ),
                "unavailable_resources": LockableResource.objects.filter(
                    Q(is_locked=True) | Q(in_maintenance=True)
                ),
                "user_locked_resources" : LockableResource.objects.filter(
                    Q(is_locked=True) & Q(signoff__startswith=request.user.username)
                ),
                "display_patch_notes" : display_patch_notes
            },
        )
    if request.method == 'POST':
        action = request.POST.get("action")  # get action
        r_lock_id = int(request.POST.get("id"))  # get ID of lockable resource
        r_lock_obj = LockableResource.objects.get(
            id=r_lock_id
        )  # get object of lockable resource
        if action == l_r_const.ACTION_RELEASE:
            r_lock_obj.release()
            messages.info(
                request, message=f"{r_lock_obj.name} has been released successfully!"
            )
        return redirect('dashboard_page')
