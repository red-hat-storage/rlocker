from django.contrib import admin
from django.contrib.admin import ModelAdmin
from rqueue.models import Rqueue


@admin.register(Rqueue)
class RqueueAdmin(ModelAdmin):
    #Display all the fields of Rqueue
    list_display = ['id', 'priority', 'time_requested', 'data', 'status', 'pended_time_descriptive']


