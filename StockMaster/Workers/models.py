from django.db import models

# Create your models here.
name = models.CharField(max_length=255)  # Product name
employeeNumber = models.IntegerField(max_length=255)  # Employee number
workArea = models.CharField(max_length=255)  # Work area of employee


