from django.db import models

from Product.models import Product


# Create your models here.

class Worker(models.Model):
    name = models.CharField(max_length=255)  # Worker's name
    workerCode = models.PositiveIntegerField()  # Worker's code
    zone = models.CharField(max_length=255)  # Worker's working zone

    def __str__(self):
        return self.name


class OutputOrder(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)  # One worker can have MULTIPLE output orders

    def GetItems(self):
        return OutputOrderItem.objects.filter(outputOrder=self)

    def __str__(self):
        return f"Orden de {self.worker} [{self.id}]"


class OutputOrderItem(models.Model):
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE)  # Products taken (One product can have multiple OutputOrderItems)
    quantity = models.PositiveIntegerField(default=0)  # Amount of products taken
    outputOrder = models.ForeignKey(OutputOrder, on_delete=models.CASCADE)  # One OutputOrder can have MULTIPLE items.

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"