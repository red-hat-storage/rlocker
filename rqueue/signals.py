from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rqueue.models import Rqueue
from rqueue.constants import Priority, Interval
from lockable_resource.models import LockableResource
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

    if created:
        data = json.loads(instance.data)
        data_id = data.get('id')
        data_signoff = data.get('signoff')

        if instance.priority == Priority.UI.value:
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
            # This case is when the locking requests are arriving from an API,
                # therefore, it should be handled from an external service.
            pass



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
        # Check if the status of the queue is changing to past tense status.
        on_going_status = ['PENDING', 'INITIALIZING']
        if not instance.status in on_going_status and rqueue.status in on_going_status:
            instance.pended_time_descriptive = instance.pending_time_descriptive
