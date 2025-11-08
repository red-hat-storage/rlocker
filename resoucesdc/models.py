from django.db import models

class ResoucesDC(models.Model):
    dc = models.CharField(max_length=100,default=None)
    storage  = models.IntegerField(default=0)
    cpu = models.IntegerField(default=0)
    memory = models.IntegerField(default=0)
    usedstorage  = models.IntegerField(default=0)
    usedcpu = models.IntegerField(default=0)
    usedmemory = models.IntegerField(default=0)
    
    def __str__(self):
        return self.dc