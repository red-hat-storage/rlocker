import json
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import utc
from rqueue.models import Rqueue
from rqueue.constants import Priority
from rqueue.utils import *


@receiver(post_save, sender=Rqueue)
def fetch_for_available_lockable_resources(sender, instance, created, **kwargs):
    '''
    The logic to add requests to queue is with the following convention:
        - We would like to prioritize requests from the UI as the highest priority, meaning 0
            Because locking directly from the UI is an immediate action that we'd like to take.
                So it makes great sense to send this request with priority zero

        - We would like to give prioritization number that is greater than zero when we try to
            search a free resource with search_string.
                There are certain rules for the prioritization.
                The rules could be found
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    '''
    data = json.loads(instance.data)
    data_id = data.get('id')
    data_signoff = data.get('signoff')
    data_name = data.get('name')

    if created and instance.priority == Priority.UI.value:
        # If there is an ID and signoff in the data, it means that the request includes a specific
        # Lockable resource that needs to be locked and NOT search_string.
        if data_id and data_signoff:
            lock_res_object = LockableResource.objects.get(id=data_id)
            lock_res_object.lock(signoff=f"{data_signoff} - Lock Type:{Priority.UI.name}")
            #Let's Customize our data before reporting it:
            del data['is_locked']
            data['priority'] = Priority.UI.value
            data['finished_time'] = str(datetime.datetime.utcnow().replace(tzinfo=utc))
            instance.report_and_delete(data_json=data)
            print(f'A queue has been deleted. \n'
                  f'Moved to Finished Queues. \n'
                  f'Resource {data_name} has been locked with priority {Priority.UI.value}')


    if created and instance.priority > Priority.UI.value:
        resource_free = check_resource_released_by_name(name=data['name'])

        #Now that the resource is free, we should not interrupt higher priority locks from it.
        rqueues_with_data_name = Rqueue.filter_from_data(key='name', value=data_name)
        if len(rqueues_with_data_name) == 1:
            #This means that this was the only rqueue for this specific resource
            #So we can lock it
            resource_free.lock(signoff=f"{data_signoff} - Lock Type:{instance.priority}")
            # Let's Customize our data before reporting it:
            del data['is_locked']
            data['finished_time'] = str(datetime.datetime.utcnow().replace(tzinfo=utc))
            instance.report_and_delete(data_json=data)
            print(f'A queue has been deleted. \n'
                  f'Moved to Finished Queues. \n'
                  f'Resource {data_name} has been locked with priority {instance.priority}')

        if len(rqueues_with_data_name) > 1:
            print('wait ... there are more queues with that wants to lock')
