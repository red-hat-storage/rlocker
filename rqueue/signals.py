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
    data_search_string = data.get('search_string')
    # We should use this as an indication to check if the Rqueue is with an associated lockable resource.
    # If ID is not None, it means that it has an associated lockable resource. Otherwise it's not.
    has_associated_resource = data_id is not None

    if created:
        if instance.priority == Priority.UI.value and data_id:
            # If there is an ID in the data, it means that the request includes a specific
            # Lockable resource that needs to be locked and NOT search_string.
            lock_res_object = LockableResource.objects.get(id=data_id)
            lock_res_object.lock(signoff=f"{data_signoff} - Lock Type:{instance.priority}")
            #Let's Customize our data before reporting it:
            customized_data = instance.customize_data(data_json=data)
            instance.report_and_delete(data_json=customized_data)
            print(f'A queue has been deleted. \n'
                  f'Moved to Finished Queues. \n'
                  f'Resource {data_name} has been locked with priority {instance.priority}')


        elif instance.priority > Priority.UI.value:
            resource_free = check_resource_released_by_name(name=data_name) if has_associated_resource else check_resource_released_by_label(label=data_search_string)

            #Now that the resource is free, we should not interrupt higher priority locks from it.
            rqueues_with_data_name = Rqueue.filter_from_data(key='name', value=resource_free.name, sort_field='priority')

            if len(rqueues_with_data_name) == 1:
                #This means that this was the only rqueue for this specific resource
                #So we can lock it
                resource_free.lock(signoff=f"{data_signoff} - Lock Type:{instance.priority}")

                # Let's Customize our data before reporting it:
                customized_data = instance.customize_data(lr_obj=resource_free)
                instance.report_and_delete(data_json=customized_data)
                print(f'A queue has been deleted. \n'
                      f'Moved to Finished Queues. \n'
                      f'Resource {data_name} has been locked with priority {instance.priority}')

            elif len(rqueues_with_data_name) > 1:
                # If there are more than one queues for the wanted resource, then we should first
                # Handle the queue that is more urgent
                # The lower priority number is, the more urgent to put this queue to finished
                # We could index the zero, since we sort by priority ascending
                prior_queue = rqueues_with_data_name[0]
                resource_free.lock(signoff=f"{data_signoff} - Lock Type:{prior_queue.priority}")

                # Let's Customize our data before reporting it:
                customized_data = prior_queue.customize_data(lr_obj=resource_free)
                prior_queue.report_and_delete(data_json=customized_data)
                print(f'A queue has been deleted. \n'
                      f'Moved to Finished Queues. \n'
                      f'Resource {data_name} has been locked with priority {prior_queue.priority}')