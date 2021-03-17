import time
import rqueue.constants as const
from lockable_resource.label_manager import LabelManager

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


def check_resource_released_by_label(label):
    counter = 0
    resource_by_label = LabelManager(label)

    while counter <= const.REQUEST_TIMEOUT // const.INTERVAL:
        resource = resource_by_label.retrieve_free_resource()
        if resource:
            return resource
        else:
            time.sleep(const.INTERVAL)
            print(f"Someone wants a resource with label {label}"
                  f"but all of them are currently locked!"
                  f"Trying in {const.INTERVAL} seconds ...")
            counter += 1