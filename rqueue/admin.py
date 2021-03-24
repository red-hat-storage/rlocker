from django.contrib import admin
from django.contrib.admin import ModelAdmin
from rqueue.models import Rqueue, FinishedQueue


@admin.register(Rqueue)
class RqueueAdmin(ModelAdmin):
    #Display all the fields of Rqueue
    list_display = ['id', 'priority', 'time_requested', 'data']



@admin.register(FinishedQueue)
class FinishedQueueAdmin(ModelAdmin):
    #Display all the fields of Rqueue
    list_display = ['rqueue_data', 'pended_time_descriptive']


