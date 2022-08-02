import json
import sys


class DescriptiveTime:
    """
    We receive the total seconds and decide a descriptive way that makes sense
        to display, depending on the total seconds amount.
    For i.e: We don't want to display 24 hours when the seconds is 86400, instead,
    it could have been nice to display 1 Day
    """

    DAY = 86400
    HOUR = 3600
    MINUTE = 60

    def __init__(self, total_seconds):
        self.total_seconds = total_seconds

        # Get the integer value for days hours and minutes
        self.days = self.total_seconds // self.DAY
        self.seconds = self.total_seconds - (self.days * self.DAY)

        self.hours = self.seconds // self.HOUR
        self.seconds = self.seconds - (self.hours * self.HOUR)

        self.minutes = self.seconds // self.MINUTE
        self.seconds = self.seconds - (self.minutes * self.MINUTE)

    @property
    def long_descriptive(self):
        if self.days > 0:
            return f"{self.days:.0f} days, {self.hours:.0f} hours, {self.minutes:.0f} minutes"

        if self.hours > 0:
            return f"{self.hours:.0f} hours, {self.minutes:.0f} minutes"

        if self.minutes > 0:
            return f"{self.minutes:.0f} minutes"

        if self.seconds >= 0:
            return "Less than a minute"

    @property
    def short_descriptive(self):
        if self.days > 0:
            return f"{self.days:.0f}d, {self.hours:.0f}h"
        if self.hours > 0:
            return f"{self.hours:.0f}h"
        if self.minutes > 0 or self.seconds >= 0:
            return "<1h"


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
