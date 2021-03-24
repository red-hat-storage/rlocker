import json
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import utc
from rqueue.models import Rqueue
from lockable_resource.models import LockableResource
from rqueue.constants import Priority

@receiver(post_save, sender=Rqueue)
def fetch_for_available_lockable_resources(sender, instance, created, **kwargs):
    if created and instance.priority == Priority.UI.value:
        data = json.loads(instance.data)
        # If there is an ID and signoff in the data, it means that the request includes a specific
        # Lockable resource that needs to be locked and NOT search_string.
        data_id =  data.get('id')
        data_signoff =  data.get('signoff')
        data_name =  data.get('name')
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
        #Here comes the complexity ...
        pass