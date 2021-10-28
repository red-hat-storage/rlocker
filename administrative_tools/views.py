from django.shortcuts import render
from lockable_resource.models import LockableResource
# Create your views here.


def index(request):
    return render(
        request,
        template_name='administrative_tools/index.html'
    )

def import_lockable_resources(request):
    pass