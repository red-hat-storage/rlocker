from django.shortcuts import render
from django.db.models import Q
from lockable_resource.models import LockableResource
from rqueue.models import Rqueue
from lockable_resource.label_manager import LabelManager

def dashboard_page(request):

    label_managers = [LabelManager(label) for label in LockableResource.get_all_labels()]
    label_managers.sort(key=lambda x: len(x.free_resources), reverse=True)
    return render(request, template_name='dashboard/index.html', context={
        'label_managers' : label_managers,
        'free_resources' : LockableResource.objects.filter(is_locked=False, in_maintenance=False),
        'unavailable_resources' : LockableResource.objects.filter(Q(is_locked=True) | Q(in_maintenance=True))
    })