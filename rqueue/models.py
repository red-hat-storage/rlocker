from django.db import models
from jsonfield import JSONField
from django.utils import timezone
from django.utils.timezone import utc
from rqueue.utils import DescriptiveTime, json_continuously_loader
from django.core.validators import MinValueValidator, MaxValueValidator
from rqueue.constants import Status
import datetime
import json


class Rqueue(models.Model):
    # Fields:
    # id - Primary key to identify each Resource Queue obj. (Auto Generated)
    # data - The data that is stored under the queue, in this case of application
    # this should be the data of the lockable resource object that is attempted to lock
    # priority - Priority level. This will allow us to prioritize different requests that are in queue.
    # time_requested - The time that the lock is requested, we should always store the current time when the
    # row is being stored to the DB
    # status - This is going to describe the status of the Rqueue, we are going to describe the different status
    # options by a list of constants from rqueue.constants
    # pended_time_descriptive - The time that the queue was pending till it deleted.
    # It is enough to receive this only descriptive and store in the DB
    # We will always store None by default till there will be an automatic update by the queue when it's done
    # description - We want to have some random text to describe each queue after it's creation
    # last_beat - We want to be sure that there is a connection opened from a client, and so, every time a client checks
    # the status of the queue, we should write down at what time it's happened. So it will prevent from orphan queues,
    # being existing in pending or initializing without a client waiting for them.

    data = JSONField()
    priority = models.IntegerField(
        default=3, validators=[MinValueValidator(0), MaxValueValidator(3)]
    )
    time_requested = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=32,
        choices=Status.CHOICES,
        default=Status.INITIALIZING,
    )
    pended_time_descriptive = models.CharField(
        max_length=1024, null=True, default=None, blank=True
    )
    description = models.CharField(max_length=2048, null=True, default=None, blank=True)
    last_beat = models.DateTimeField(blank=True, null=True, default=None)

    @property
    def bootstrap_classes(self):
        """
        Instance Property
        Includes additional key&values about the status of the Rqueue obj
        Depending on the status, we want to include different styling for the HTML template
        This approach is similar to lockable_resources status_properties property

        :returns: Dictionary
        """
        bts_classes = {
            Status.FAILED: {"loader": "loader-failed", "btn": "btn-primary"},
            Status.ABORTED: {"loader": "loader-aborted", "btn": "btn-primary"},
            Status.ALMOST_FINISHED: {
                "loader": "loader-almost-finished",
                "btn": "btn-primary",
            },
            Status.FINISHED: {"loader": "loader-finished", "btn": "btn-primary"},
            Status.INITIALIZING: {
                "loader": "loader-initializing",
                "btn": "btn-primary",
            },
            Status.PENDING: {"loader": "loader-pending", "btn": "btn-primary"},
        }
        return bts_classes.get(self.status)

    @property
    def pending_time(self):
        """
        Instance property to create a nicer message about time displaying
            For i.e: instead of showing 2700, we could display 45 minutes
        :return str  Descriptive output of time by knowing the total seconds
        """
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        timediff = now - self.time_requested
        return timediff

    @property
    def pending_time_descriptive(self):
        """
        Instance property to create a nicer message about time displaying
            For i.e: instead of showing 2700, we could display 45 minutes
        :return str  Descriptive output of time by knowing the total seconds
        """
        return DescriptiveTime(self.pending_time.total_seconds()).long_descriptive

    def __str__(self):
        # Here we override each object definition
        return f"Rqueue{self.id}:P-{self.priority}"

    @property
    def data_as_json(self):
        try:
            parsed_dict = json_continuously_loader(self.data)
            parsed_dict = dict(parsed_dict)
            return parsed_dict.items()
        except Exception as e:
            return str(e)

    def report_finish(self):
        """
        Instance Method
        We want to change the status from the default PENDING, to finished because
            the queue finished to wait and a lockable resource is locked
        :return: None
        """
        # TODO: remove changing the pended time descriptive, as the signal does this already!
        self.status = Status.FINISHED
        self.pended_time_descriptive = self.pending_time_descriptive
        self.save()

    def add_to_data_json(self, json_to_add=None, **kwargs):
        """
        Instance Method
        Will handle to add additional key values to the JSON where we store data
            about the locked request
        Sometimes the data may be passed as pure JSON, or sometimes as key value dict
        :param json_to_add: None by default - Optional to add data by json
        :param kwargs: key value pairs to add
        :return:
        """
        data = json_continuously_loader(self.data)
        if json_to_add:
            json_to_dict = json_continuously_loader(json_to_add)
            # Merge dicts:
            data.update(json_to_dict)
            self.data = data

        if not json_to_add:
            for key, value in kwargs.items():
                data[key] = value
            # Update the Rqueue object
            self.data = data

        self.save()

    def get_data_value(self, key):
        data = dict(json_continuously_loader(self.data))
        return data.get(key, "")

    @property
    def name(self):
        return self.get_data_value("name")

    @property
    def signoff(self):
        return self.get_data_value("signoff")

    @property
    def label(self):
        return self.get_data_value("label")

    @property
    def link(self):
        return self.get_data_value("link")

    class Meta:
        # Here you can put more descriptive to display in Admin
        verbose_name_plural = "Requests in Queue"
