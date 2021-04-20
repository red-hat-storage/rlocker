import time
import json
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


def json_load_twice(json_string):
    '''
    WORKAROUND:
        Currently we don't know how to handle json.loads()
            Because in PostgresDB the json.loads() still remains the object as string
            So Sometimes the json.loads should be tried twice()
    :param json_string:
    :return:
    '''
    loaded_json = json.loads(json_string)
    if type(loaded_json) == str:
        loaded_json_second_attempt = json.loads(json_string)
        # This should be a dictionary now, so let's test this out by executing the built-in convertion to it:
        dict(loaded_json_second_attempt)  # Should fail if it is still not a dict
        return loaded_json_second_attempt

    elif type(loaded_json) == dict:
        return loaded_json

    else:
        raise TypeError
