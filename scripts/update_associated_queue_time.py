from lockable_resource.models import LockableResource


def run():
    """
    Update all the Lockable Resource time requested from the rqueue.time_requested

    :return:
    """

    lrs = LockableResource.objects.all().filter(is_locked=True)
    for lr in lrs:
        if lr.associated_queue:
            print(lr.name, lr.associated_queue.id, lr.associated_queue.time_requested)
            if not lr.locked_time:
                lr.locked_time = lr.associated_queue.time_requested
                lr.save()


