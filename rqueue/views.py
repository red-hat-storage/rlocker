from django.shortcuts import render
from rqueue.models import Rqueue


def pending_requests_page(request):
    rqueues = Rqueue.objects.all().order_by('priority')
    return render(request,
                  template_name='rqueue/pending_requests.html',
                  context={'rqueues':rqueues})