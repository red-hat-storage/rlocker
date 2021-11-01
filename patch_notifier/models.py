from django.db import models
from django.contrib.auth.models import User


class FirstVisit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_visited = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}_" + "1" if self.is_visited else "0"
