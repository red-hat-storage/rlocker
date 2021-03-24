from django.shortcuts import render
from rqueue.models import Rqueue, FinishedQueue


def pending_requests_page(request):
    rqueues = Rqueue.objects.all().order_by('priority')
    return render(request,
                  template_name='rqueue/pending_requests.html',
                  context={'rqueues':rqueues})

def finished_requests_page(request):
    finished_requests = FinishedQueue.objects.all().order_by('-id')
    return render(request,
                  template_name='rqueue/finished_requests.html',
                  context={'finishedqueues':finished_requests})