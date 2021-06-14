from django.shortcuts import render, redirect
from django.contrib import messages
from rqueue.models import Rqueue
from rqueue.constants import Status


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
        # We do enter here when a priority is changed!:
        rqueue_id = request.POST.get("id")
        rqueue_changed_priority = request.POST.get("priority")
        rqueue_obj = Rqueue.objects.get(id=rqueue_id)

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
        return redirect("pending_requests_page")


def finished_requests_page(request):
    finished_requests = Rqueue.objects.filter(
        status__in=Status.PAST_STATUS_OPTIONS
    ).order_by("-id")

    return render(
        request,
        template_name="rqueue/finished_requests.html",
        context={"finishedqueues": finished_requests},
    )


def rqueue_more_info(request, slug):
    rqueue = Rqueue.objects.get(id=slug)
    return render(
        request,
        template_name="rqueue/rqueue_more_info.html",
        context={"rqueue": rqueue},
    )
