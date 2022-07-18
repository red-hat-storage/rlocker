import lockable_resource.constants as const
import rqueue.constants as const_rqueue
from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponse
from lockable_resource.models import *
from lockable_resource.query_param_manager import QueryParamManager
from lockable_resource.action_manager import LRActionObjectsHandler


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
        # Get Desired Action:
        desired_action = request.POST.get("action")
        action_handler = LRActionObjectsHandler.SUPPORTED_ACTION_OBJECTS.get(desired_action)
        # Create an instance of the desired action handler
        action_obj = action_handler(request)
        action_obj.complete_action()

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
