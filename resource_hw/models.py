from django.db import models

class ResouceHW(models.Model):
    dc_name = models.CharField(max_length=100,default=None)
    storage_max  = models.IntegerField(default=0)
    cpu_max = models.IntegerField(default=0)
    memory_max = models.IntegerField(default=0)
    
    storage_used  = models.IntegerField(default=0)
    cpu_used = models.IntegerField(default=0)
    memory_used = models.IntegerField(default=0)

    def __str__(self):
        return self.dc_name
