import json
import sys


def get_time_descriptive(total_seconds):
    """
    We receive the total seconds and decide a descriptive way that makes sense
        to display, depending on the total seconds amount.
    For i.e: We don't want to display 24 hours when the seconds is 86400, instead,
    it could have been nice to display 1 Day
    :param total_seconds:
    :return:
    """
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


def json_continuously_loader(json_string, attempts=10):
    """
    WORKAROUND:
        Currently we don't know how to handle json.loads()
            Because in PostgresDB the json.loads() still might remain as string although we try to use it as dictionary
            So Sometimes the json.loads should be tried more than once.
    :param json_string:
    :return:
    """
    if type(json_string) == dict:
        return json_string

    loaded_json = None
    attempts = list(range(1, attempts + 1, 1))
    for attempt in attempts:
        try:
            loaded_json = json.loads(json_string)
            dict(
                loaded_json
            )  # Should fail with value error if this is still NOT a dictionary
            # DEBUG LINE AND COULD BE DELETED:
            print(f"Succeeded to parse json at attempt number {attempt}")
            return loaded_json  # If it is a python dictionary, lets return it
        except ValueError:
            if attempt != attempts[-1]:
                print(
                    "The loaded json is still not a dictionary, trying to parse again the same json ... \n"
                )
                json_string = loaded_json
                print(loaded_json)
            else:
                # If after 10 tries, we we're not able to return loaded_json, something went wrong.
                # Let's RAISE the original error
                print("Unexpected error:", sys.exc_info()[0])
                raise
