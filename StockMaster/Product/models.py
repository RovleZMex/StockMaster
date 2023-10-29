from django.db import models
from simple_history.models import HistoricalRecords


# Represents all different products registered in the DB
class Product(models.Model):
    name = models.CharField(max_length=255)  # Product name
    SKU = models.CharField(max_length=255, unique=True)  # Product SKU
    price = models.FloatField(default=0.0)  # Product price
    quantity = models.PositiveIntegerField(default=0)  # Current product stock
    image = models.ImageField(upload_to='uploads/% Y/% m/% d/', blank=True)  # Product Image
    threshold = models.PositiveIntegerField(default=0)  # Low stock threshold
    category = models.CharField(max_length=255, choices=[
        ('ELE', 'Eléctrico'),  # Different categories per product
        ('PLU', 'Plomería'),
        ('OFF', 'Oficina'),
        ('CLE', 'Limpieza')
    ])
    isExternal = models.BooleanField(default=False)  # If acquired outside the institution
    history = HistoricalRecords()  # Used to manage history modifications

    def isLowStock(self):
        return self.quantity<=self.threshold


    def __str__(self):
        return self.name
