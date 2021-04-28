from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rqueue.models import Rqueue
from rqueue.constants import Priority, Interval
from lockable_resource.models import LockableResource
from rqueue.utils import *
import time
from lockable_resource.label_manager import LabelManager



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

    if created:
        data = json.loads(instance.data)
        data_id = data.get('id')
        data_signoff = data.get('signoff')
        data_name = data.get('name')
        data_label = data.get('label')
        # We should use this as an indication to check if the Rqueue is with an associated lockable resource.
        # If ID is not None, it means that it has an associated lockable resource. Otherwise it's not.
        has_associated_resource = data_id is not None

        if instance.priority == Priority.UI.value and data_id:
            # If there is an ID in the data, it means that the request includes a specific
            # Lockable resource that needs to be locked and NOT search_string.
            lock_res_object = LockableResource.objects.get(id=data_id)
            lock_res_object.lock(signoff=data_signoff)
            instance.add_to_data_json(json_to_add=lock_res_object.json_parse())
            instance.report_finish()
            print(f'A queue has been changed to status FINISHED. \n'
                  f'Resource {lock_res_object.name} has been locked with priority {instance.priority}')


        elif instance.priority > Priority.UI.value:
            # We should be able to handle here multiple request queues in parallel.
            # We should sort them by urgency level, the lower the priority is.
            # The more urgent to handle the request in queue

            while True:
                #Let's see how we are going to check Requests in queue, by name or label
                requests_in_queue = Rqueue.pending_queues_by_jsondata(key='name', value=data_name, sort_field='priority') \
                    if has_associated_resource \
                    else \
                    Rqueue.pending_queues_by_jsondata(key='label', value=data_label, sort_field='priority')

                if requests_in_queue[0] == instance:
                    print(f"The Request with ID {instance.id} is next in turn!")
                    #If this is the first queue that waits, let's try to understand for what it waits
                    if has_associated_resource:
                        requested_resource = LockableResource.objects.filter(name=data_name, is_locked=False, in_maintenance=False).first()
                    else:
                        label_manager = LabelManager(label=data_label)
                        requested_resource = label_manager.retrieve_free_resource(not_exist_ok=True)

                    if requested_resource:
                        requested_resource.lock(signoff=data_signoff)
                        instance.add_to_data_json(json_to_add=requested_resource.json_parse())
                        instance.report_finish()
                        print(f'A queue has been changed to status FINISHED. \n'
                              f'Resource {requested_resource.name} has been locked with priority {instance.priority}')
                        break

                    else:
                        print(f"Waiting {Interval.RESOURCE_FREE_WAIT} seconds till next try ...")
                        time.sleep(Interval.RESOURCE_FREE_WAIT)

                else:
                    print(f"A Queue Request is received with ID {instance.id} \n"
                          f"Currently, there are more than one requests that wants the same resource/s. \n"
                          f"Once the request with ID {instance.id} will be next, it will notify.\n"
                          f"Current status: {requests_in_queue}")
                    time.sleep(Interval.QUEUE_TURN_WAIT)

    if not created:
        pass

@receiver(pre_save, sender=Rqueue)
def give_pended_time_value_after_status_change(sender, instance, **kwargs):
    '''
    A signal that will allow to edit the pended time descriptive as soon as
        the status of a queue is being changed to something that is NOT Pending
    That is important, because it describes the time that the queue waited, before it got
    Finished, Aborted or Failed
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    '''
    try:
        rqueue=sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass

    else:
        if not instance.status == 'PENDING' and rqueue.status == 'PENDING':   #If Rqueue is being NOT EQUAL TO PENDING
            instance.pended_time_descriptive = instance.pending_time_descriptive
