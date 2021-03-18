from django.db import models
from jsonfield import JSONField
from django.utils import timezone
from django.utils.timezone import utc
from rqueue.utils import get_time_descriptive
import datetime

class Rqueue(models.Model):
    #Fields:
        # id - Primary key to identify each Resource Queue obj. (Auto Generated)
        # data - The data that is stored under the queue, in this case of application
            #this should be the data of the lockable resource object that is attempted to lock
        # priority - Priority level. This will allow us to prioritize different requests that are in queue.
        # time_requested - The time that the lock is requested, we should always store the current time when the
            #row is being stored to the DB

    data = JSONField()
    priority = models.IntegerField()
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
        return get_time_descriptive(timediff.seconds)

    def __str__(self):
        #Here we override each object definition
        return f'Rqueue {self.id}'

    class Meta:
        #Here you can put more descriptive to display in Admin
        verbose_name_plural = "Requests in Queue"