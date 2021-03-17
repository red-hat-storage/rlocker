from django.db import models
from jsonfield import JSONField
from django.utils import timezone


class Rqueue(models.Model):
    data = JSONField()
    priority = models.IntegerField()
    time_requested = models.DateTimeField(default=timezone.now)

    def __str__(self):
        #Here we override each object definition
        return f'Rqueue {self.id}'

    class Meta:
        #Here you can put more descriptive to display in Admin
        verbose_name_plural = "Requests in Queue"