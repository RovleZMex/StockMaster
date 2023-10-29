from django.db import models


# Create your models here.
class Worker(models.Model):
    name = models.CharField(max_length=255)  # Employee name
    employeeNumber = models.IntegerField(unique=True)  # Employee number
    workArea = models.CharField(max_length=255)  # Work area of employee

    def __str__(self):
        return self.name
