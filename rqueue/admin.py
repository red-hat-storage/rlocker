from django.contrib import admin
from django.contrib.admin import ModelAdmin
from rqueue.models import Rqueue


@admin.register(Rqueue)
class RqueueAdmin(ModelAdmin):
    #Display all the fields of Rqueue
    list_display = [str(field).split('.')[-1] for field in Rqueue._meta.get_fields()]