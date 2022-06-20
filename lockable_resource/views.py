import lockable_resource.constants as const
import rqueue.constants as const_rqueue
from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponse
from lockable_resource.models import *
from rqueue.models import Rqueue
from rqueue.constants import Priority
from lockable_resource.query_param_manager import QueryParamManager


def lockable_resources_page(request):
    if request.method == "GET":
        query_params = request.GET
        if query_params:
            qp_key = list(dict(query_params).keys())[0]
            qp_val = list(dict(query_params).values())[0][0]
            q_manager = QueryParamManager(qp_key, qp_val)
            data = q_manager.handle_key()

            return HttpResponse(data, content_type="text/plain")

        # Display regularly the page if no query_params added
        lockable_resources = LockableResource.objects.all().order_by("name")
        return render(
            request,
            template_name="lockable_resource/all.html",
            context={"lockable_resources": lockable_resources},
        )

    if request.method == "POST":
        action = request.POST.get("action")  # get action
        r_lock_id = int(request.POST.get("id"))  # get ID of lockable resource
        r_lock_obj = LockableResource.objects.get(
            id=r_lock_id
        )  # get object of lockable resource

        if action == const.ACTION_LOCK:
            signoff = request.POST.get(f"signoff-{r_lock_id}")  # get signoff
            # Create a queue for this lock request with priority 0

            new_queue = Rqueue(
                priority=Priority.UI.value,
                data=r_lock_obj.json_parse(
                    # We'd like to parse a new json with the requested signoff from the POST request
                    override_signoff=True,
                    signoff=signoff,
                ),
                status=const_rqueue.Status.INITIALIZING
            )
            new_queue.save()
            messages.info(
                request,
                message=f"{r_lock_obj.name} has been sent to Pending requests"
                f" with Priority {new_queue.priority}! Signoff: {signoff}",
            )

        if action == const.ACTION_RELEASE:
            r_lock_obj.release()
            messages.info(
                request, message=f"{r_lock_obj.name} has been released successfully!"
            )

        if action == const.ACTION_MAINTENANCE_MODE_ENTER:
            r_lock_obj.in_maintenance = True
            r_lock_obj.save()
            messages.info(
                request,
                message=f"{r_lock_obj.name} has been Entered to Maintenance Mode!",
            )

        if action == const.ACTION_MAINTENANCE_MODE_EXIT:
            r_lock_obj.in_maintenance = False
            r_lock_obj.save()
            messages.info(
                request,
                message=f"{r_lock_obj.name} has been Exited from Maintenance Mode! Resources now could be locked/released as usual!",
            )

        return redirect("lockable_resources_page")

def lockable_resource_more_info(request, slug):
    lr = LockableResource.objects.get(id=slug)
    # Gather the next & previous Lockable resource and send as context
    # This is useful in this template only for navigating
    next_lr = lr.next_obj()
    previous_lr = lr.previous_obj()
    return render(
        request,
        template_name="lockable_resource/lockable_resource_more_info.html",
        context={
            "lockable_resource": lr,
            "next_lockable_resource": next_lr,
            "previous_lockable_resource": previous_lr,
        },
    )