from django.db import models
from simple_history.models import HistoricalRecords
from django.utils import timezone


# Represents all different products registered in the DB
class Product(models.Model):
    name = models.CharField(max_length=255)  # Product name
    SKU = models.CharField(max_length=255)  # Product SKU
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


class Worker(models.Model):
    name = models.CharField(max_length=255)  # Worker's name
    workerCode = models.PositiveIntegerField()  # Worker's code
    zone = models.CharField(max_length=255)  # Worker's working zone

    def __str__(self):
        return self.name


class OutputOrder(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)  # One worker can have MULTIPLE output orders
    creation_date = models.DateTimeField(auto_now_add=True)  # Gets the date an order is made

    def GetItems(self):
        return OutputOrderItem.objects.filter(outputOrder=self)

    def __str__(self):
        return f"Orden de {self.worker} [{self.pk}]"


class OutputOrderItem(models.Model):
    # Products taken (One product can have multiple OutputOrderItems)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)  # Amount of products taken

    # One OutputOrder can have MULTIPLE items.
    outputOrder = models.ForeignKey(OutputOrder, on_delete=models.CASCADE, related_name='items')

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
