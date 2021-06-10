#This file will help us to have more context declared.
#Therefore, we could access the values (by referring to their keys)
    #using the jinja syntax from ALL the HTML templates

from rqueue.models import Rqueue
from rqueue.constants import Status
def rqueue_context_processors(request):
    return {
        'pending_requests' : len(Rqueue.objects.filter(status__in=Status.PRESENT_STATUS_OPTIONS)) > 0,
        'pending_requests_amount' : len(Rqueue.objects.filter(status__in=Status.PRESENT_STATUS_OPTIONS)),
    }