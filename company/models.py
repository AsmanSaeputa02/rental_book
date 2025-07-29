
from django.db import models

class Company(models.Model):
    cid = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
