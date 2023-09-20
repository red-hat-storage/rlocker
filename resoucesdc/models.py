from django.db import models

class ResoucesDC(models.Model):
    dc = models.CharField(max_length=100)
    storage  = models.IntegerField()
    cpu = models.IntegerField()
    memory = models.IntegerField()
    
    def __str__(self):
        return self.dc