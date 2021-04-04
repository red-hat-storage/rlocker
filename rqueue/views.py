from django.shortcuts import render, redirect
from rqueue.models import Rqueue
from rqueue.constants import Status

def pending_requests_page(request):
    if request.method == 'GET':
        rqueues = Rqueue.objects.filter(status=Status.PENDING).order_by('priority')
        return render(request,
                      template_name='rqueue/pending_requests.html',
                      context={'rqueues':rqueues})

    if request.method == 'POST':
        rqueue_id = request.POST.get('id')
        rqueue_changed_priority = request.POST.get('priority')
        rqueue_obj = Rqueue.objects.get(id=rqueue_id)
        rqueue_obj.priority = int(rqueue_changed_priority)
        rqueue_obj.save()
        return redirect('pending_requests_page')

def finished_requests_page(request):
    finished_requests =Rqueue.objects.filter(status=Status.FINISHED).order_by('-id')
    return render(request,
                  template_name='rqueue/finished_requests.html',
                  context={'finishedqueues':finished_requests})