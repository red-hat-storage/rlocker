from django.db import models

class ResoucesDC(models.Model):
    dc = models.CharField(max_length=100)
    storage  = models.CharField(max_length=100)
    cpu = models.CharField(max_length=100)
    memory = models.CharField(max_length=100)
    usedstorage  = models.CharField(max_length=100)
    usedcpu = models.CharField(max_length=100)
    usedmemory = models.CharField(max_length=100)
    
    def __str__(self):
        return self.dc