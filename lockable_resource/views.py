import lockable_resource.constants as const
from django.contrib import messages
from django.shortcuts import render, redirect
from lockable_resource.models import *


def lockable_resources_page(request):
    if request.method == 'GET':
        lockable_resources = LockableResource.objects.all()
        return render(request, template_name='lockable_resource/all.html',
                  context={"lockable_resources" : lockable_resources })

    if request.method == 'POST':
        action = request.POST.get('action') # get action
        r_lock_id = int(request.POST.get('id'))  # get ID of lockable resource
        r_lock_obj = LockableResource.objects.get(id=r_lock_id) #get object of lockable resource

        if action == const.ACTION_LOCK:
            signoff = request.POST.get(f'signoff-{r_lock_id}') # get signoff
            r_lock_obj.lock(signoff=signoff)
            messages.info(request, message=f"{r_lock_obj.name} has been locked successfully! Signoff: {r_lock_obj.signoff}")

        if action == const.ACTION_RELEASE:
            r_lock_obj.release()
            messages.info(request, message=f"{r_lock_obj.name} has been released successfully!")


        return redirect('lockable_resources_page')
