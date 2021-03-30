import time
import rqueue.constants as const
from lockable_resource.models import LockableResource

def get_time_descriptive(total_seconds):
    '''
    We receive the total seconds and decide a descriptive way that makes sense
        to display, depending on the total seconds amount.
    For i.e: We don't want to display 24 hours when the seconds is 86400, instead,
    it could have been nice to display 1 Day
    :param total_seconds:
    :return:
    '''
    seconds_in_day = 86400
    seconds_in_hour = 3600
    seconds_in_minute = 60


    days = total_seconds // seconds_in_day
    seconds = total_seconds - (days * seconds_in_day)

    hours = seconds // seconds_in_hour
    seconds = seconds - (hours * seconds_in_hour)

    minutes = seconds // seconds_in_minute
    seconds = seconds - (minutes * seconds_in_minute)

    if days > 0:
        return f"{days:.0f} days, {hours:.0f} hours, {minutes:.0f} minutes"

    if hours > 0:
        return f"{hours:.0f} hours, {minutes:.0f} minutes"

    if minutes > 0:
        return f"{minutes:.0f} minutes"

    if seconds > 0:
        return f"Less than a minute"


def check_resource_released_by_name(name):
    counter = 0
    while counter <= const.REQUEST_TIMEOUT // const.INTERVAL:
        resource = LockableResource.objects.get(name=name)
        if resource.is_locked:
            time.sleep(const.INTERVAL)
            print(f"Someone wants the resource {name} "
                  f"but it is currently locked! \n"
                  f"Trying in {const.INTERVAL} seconds ...")
            counter += 1
        else:
            return resource

def check_resource_released_by_label(label):
    counter = 0
    while counter <= const.REQUEST_TIMEOUT // const.INTERVAL:
        resources = LockableResource.objects.filter(labels_string__icontains=label)
        #Here write a logic that will check if all resources are locked
        if len(set([resource.is_locked for resource in resources])) == 1:
            time.sleep(const.INTERVAL)
            print(f"Someone wants a resource with label {label} "
                  f"but all of them are currently locked! \n"
                  f"Trying in {const.INTERVAL} seconds ...")
            counter += 1
        else:
            #Something got free ...
            pass
