from django.db import models

from Product.models import Product
from Workers.models import Worker


class OutputOrder(models.Model):
    """
    Represents an output order in the system.

    Attributes:
        worker (ForeignKey): The worker associated with the output order.
        date_created (DateTimeField): The date and time when the order was created.
    """

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    """
    ForeignKey: The worker associated with the output order.
    """

    date_created = models.DateTimeField(auto_now_add=True)
    """
    DateTimeField: The date and time when the order was created.
    """

    def GetItems(self):
        """
        Retrieve the items associated with the output order.

        Returns:
            QuerySet: The items associated with the output order.
        """
        return OutputOrderItem.objects.filter(outputOrder=self)

    def GetTotal(self):
        """
        Calculate the total cost of the output order.

        Returns:
            float: The total cost of the output order.
        """
        total = 0
        for item in self.GetItems():
            total += item.quantity * item.product.price
        return round(total, 3)

    def __str__(self):
        """
        Returns the string representation of the output order.

        Returns:
            str: A string representation of the output order.
        """
        return f"Orden de {self.worker} [{self.id}]"


class OutputOrderItem(models.Model):
    """
    Represents an item in an output order.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    """
    ForeignKey: The product associated with the output order item.
    """

    quantity = models.PositiveIntegerField(default=0)
    """
    PositiveIntegerField: The quantity of the product in the output order item.
    """

    outputOrder = models.ForeignKey(OutputOrder, on_delete=models.CASCADE)
    """
    ForeignKey: The output order associated with the item.
    """

    def __str__(self):
        """
        Returns the string representation of the output order item.

        Returns:
            str: A string representation of the output order item.
        """
        return f"{self.product.name} - {self.quantity}"
