import lockable_resource.constants as const
import rqueue.constants as const_rqueue
from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Q
from lockable_resource.models import *
from lockable_resource.query_param_manager import QueryParamManager
from lockable_resource.action_manager import LRActionObjectsHandler


def lockable_resources_page(request):
    if request.method == "GET":
        query_params = request.GET

        # Handle special query params first (like view_as=yaml)
        # These take precedence over status filtering
        for qp_key in QueryParamManager.SUPPORTED_QUERY_PARAMS:
            if qp_key in query_params:
                qp_val = query_params.get(qp_key)
                q_manager = QueryParamManager(qp_key, qp_val)
                data = q_manager.handle_key()
                if data is not None:
                    return HttpResponse(data, content_type="text/plain")

        # Get filter parameters
        status_filter = query_params.get("status", "all")
        provider_filter = query_params.get("provider", "")
        search_text = query_params.get("search", "")

        # Start with base queryset
        lockable_resources = LockableResource.objects.all()

        # Apply status filter
        if status_filter == "free":
            lockable_resources = lockable_resources.filter(
                is_locked=False, in_maintenance=False
            )
        elif status_filter == "locked":
            lockable_resources = lockable_resources.filter(is_locked=True)
        elif status_filter == "maintenance":
            lockable_resources = lockable_resources.filter(in_maintenance=True)
        else:
            status_filter = "all"

        # Apply provider filter
        if provider_filter:
            lockable_resources = lockable_resources.filter(provider=provider_filter)

        # Apply search filter across multiple fields
        if search_text:
            lockable_resources = lockable_resources.filter(
                Q(name__icontains=search_text)
                | Q(labels_string__icontains=search_text)
                | Q(signoff__icontains=search_text)
                | Q(description__icontains=search_text)
            )

        lockable_resources = lockable_resources.order_by("name")

        # Get all unique providers for the dropdown
        all_providers = (
            LockableResource.objects.values_list("provider", flat=True)
            .distinct()
            .order_by("provider")
        )

        return render(
            request,
            template_name="lockable_resource/all.html",
            context={
                "lockable_resources": lockable_resources,
                "status_filter": status_filter,
                "provider_filter": provider_filter,
                "search_text": search_text,
                "all_providers": all_providers,
                "show_filters": True,
            },
        )

    if request.method == "POST":
        # Get Desired Action:
        desired_action = request.POST.get("action")
        action_handler = LRActionObjectsHandler.SUPPORTED_ACTION_OBJECTS.get(
            desired_action
        )
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
