from django.db import models

from Product.models import Product
from Workers.models import Worker


class OutputOrder(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)  # One worker can have MULTIPLE output orders
    date_created = models.DateTimeField(auto_now_add=True)

    def GetItems(self):
        return OutputOrderItem.objects.filter(outputOrder=self)

    def GetTotal(self):
        total = 0
        for item in self.GetItems():
            total += item.quantity * item.product.price
        return round(total, 3)

    def GetQuantity(self):
        total = 0
        for item in self.GetItems():
            total += item.quantity
        return total

    def __str__(self):
        return f"Orden de {self.worker} [{self.id}]"


class OutputOrderItem(models.Model):
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE)  # Products taken (One product can have multiple OutputOrderItems)
    quantity = models.PositiveIntegerField(default=0)  # Amount of products taken
    outputOrder = models.ForeignKey(OutputOrder, on_delete=models.CASCADE)  # One OutputOrder can have MULTIPLE items.

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
