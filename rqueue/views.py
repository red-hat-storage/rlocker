import rqueue.constants as const
from django.shortcuts import render, redirect
from django.contrib import messages
from rqueue.models import Rqueue
from rqueue.constants import Status
from django.core.paginator import Paginator


def pending_requests_page(request):
    if request.method == "GET":
        rqueues = Rqueue.objects.filter(
            status__in=Status.PRESENT_STATUS_OPTIONS
        ).order_by("priority")
        return render(
            request,
            template_name="rqueue/pending_requests.html",
            context={"rqueues": rqueues},
        )

    if request.method == "POST":
        # Those could be outside the if conditionals
        rqueue_id = request.POST.get("rqueue_id")
        rqueue_obj = Rqueue.objects.get(id=rqueue_id)

        # We do enter here when a priority is changed!:
        if request.POST.get('action') == "change_priority":
            rqueue_changed_priority = request.POST.get("priority_value")
            # Get the previous priority before changing it to send a message:
            previous_priority = rqueue_obj.priority

            rqueue_obj.priority = int(rqueue_changed_priority)
            rqueue_obj.save()
            messages.info(
                request,
                message=f"Queue with ID {rqueue_obj.id} has been changed! \n"
                f"Previous Priority: {previous_priority} \n"
                f"New Priority: {rqueue_obj.priority}",
            )
        # We do enter here when there is request to abort a request in queue
        if request.POST.get('action') == const.Status.ABORTED.lower():
            rqueue_obj.status = const.Status.ABORTED
            rqueue_obj.description = f"Manual Abortion by: {request.user.username}"
            rqueue_obj.save()
            messages.info(
                request,
                message=f"Queue with ID {rqueue_obj.id} has been ABORTED!"
            )


        return redirect("pending_requests_page")

def finished_requests_page(request):
    finished_requests = Rqueue.objects.filter(
        status__in=Status.PAST_STATUS_OPTIONS
    ).order_by("-id")
    # Initialize the paginator object, which will split the given objects:
    paginator = Paginator(finished_requests, const.DISPLAY_COUNT_PER_PAGE)
    # Current page number:
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        template_name="rqueue/finished_requests.html",
        context={"finishedqueues": page_obj},
    )


def rqueue_more_info(request, slug):
    rqueue = Rqueue.objects.get(id=slug)
    return render(
        request,
        template_name="rqueue/rqueue_more_info.html",
        context={"rqueue": rqueue},
    )
