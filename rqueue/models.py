from django.db import models
from jsonfield import JSONField
from django.utils import timezone
from django.utils.timezone import utc
from rqueue.utils import get_time_descriptive
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime
import json

class Rqueue(models.Model):
    #Fields:
        # id - Primary key to identify each Resource Queue obj. (Auto Generated)
        # data - The data that is stored under the queue, in this case of application
            #this should be the data of the lockable resource object that is attempted to lock
        # priority - Priority level. This will allow us to prioritize different requests that are in queue.
        # time_requested - The time that the lock is requested, we should always store the current time when the
            #row is being stored to the DB

    data = JSONField()
    priority = models.IntegerField(
        default=3,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(3)
        ]
    )
    time_requested = models.DateTimeField(default=timezone.now)

    @property
    def pending_time(self):
        '''
        Instance property to create a nicer message about time displaying
            For i.e: instead of showing 2700, we could display 45 minutes
        :return str  Descriptive output of time by knowing the total seconds
        '''
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        timediff = now - self.time_requested
        return timediff

    @property
    def pending_time_descriptive(self):
        '''
        Instance property to create a nicer message about time displaying
            For i.e: instead of showing 2700, we could display 45 minutes
        :return str  Descriptive output of time by knowing the total seconds
        '''
        return get_time_descriptive(self.pending_time.seconds)

    def __str__(self):
        #Here we override each object definition
        return f'Rqueue {self.id}'

    def report_and_delete(self, data_json):
        report = FinishedQueue(
            rqueue_data=data_json,
            pended_time_descriptive=self.pending_time_descriptive # We'd like to store the exact pended time as a DB row
        )
        report.save()

        self.delete()

    @staticmethod
    def filter_from_data(key, value, sort_field='priority'):
        '''
        Static method to filter Rqueue objects from the given key
            from the JSONFIELD
        It is a great idea to return this sorted by priority ascending
            by default
        :param key:
        :param value:
        :param sort_field:
        :return: Rqueue object/s
        '''
        filter_matches = []
        for rqueue in Rqueue.objects.all():
            if json.loads(rqueue.data).get(key) == value:
                filter_matches.append(rqueue)

        if filter_matches != []:
            return sorted(filter_matches, key=lambda x: (int(getattr(x, sort_field)),x.time_requested))
        else:
            return None

    def customize_data(self, data_json=None, lr_obj=None):
        '''
        Instance Method
        Sometimes we need to customize a data before we report it and do
            something with it, because not everything is necessary for some actions
        Specially when we move the data to being a finished queue
        :param data_json:
        :return data_json
        '''
        data_json = data_json if data_json else json.loads(lr_obj.json_parse())
        del data_json['is_locked']
        data_json['finished_time'] = str(datetime.datetime.utcnow().replace(tzinfo=utc))
        return data_json

    class Meta:
        #Here you can put more descriptive to display in Admin
        verbose_name_plural = "Requests in Queue"

class FinishedQueue(models.Model):
    #Fields:
        #id - Primary key to identify each Finished queue obj. (Auto Generated)
        #rqueue_data - JSON field with all the data from the request queue
            # We want to keep this JSON field so that we don't have to update multiple fields
                # in multiple models every time.
        #pended_time_descriptive - The time that the queue was pending till it deleted.
            #It is enough to receive this only descriptive

    rqueue_data = JSONField()
    pended_time_descriptive = models.CharField(max_length=1024, null=True, default=None)


    def __str__(self):
        #Here we override each object definifion
        return f'FinishedQueue {self.id}'

    class Meta:
        #Here you can put more descriptive to display in Admin
        verbose_name_plural = "Finished Queues"