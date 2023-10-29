from django.db import models

from Product.models import Product


# Create your models here.

class InputOrder(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    specialNotes = models.TextField(max_length=600, blank=True)

    def GetItems(self):
        return InputOrderItem.objects.filter(inputOrder=self)

    def GetTotal(self):
        total = 0
        for item in self.GetItems():
            total += item.quantity * item.product.price
        return round(total, 3)

    def __str__(self):
        return f"Compra de {self.date_created}"


class InputOrderItem(models.Model):
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE)  # Products taken (One product can have multiple OutputOrderItems)
    quantity = models.PositiveIntegerField(default=0)  # Amount of products taken
    inputOrder = models.ForeignKey(InputOrder, on_delete=models.CASCADE)  # One OutputOrder can have MULTIPLE items.

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
