from django.db import models

from Product.models import Product


class InputOrder(models.Model):
    """
    Represents an input order in the system.
    """

    date_created = models.DateTimeField(auto_now_add=True)
    """DateTimeField: The date and time when the order was created."""

    specialNotes = models.TextField(max_length=600, blank=True)

    isExternal = models.BooleanField(default=False)

    def GetItems(self):
        """
        Retrieve the items associated with the input order.

        Returns:
            QuerySet: The items associated with the input order.
        """
        return InputOrderItem.objects.filter(inputOrder=self)

    def GetTotal(self):
        """
        Calculate the total cost of the input order.

        Returns:
            float: The total cost of the input order.
        """
        total = 0
        for item in self.GetItems():
            total += item.quantity * item.product.price
        return round(total, 2)

    def __str__(self):
        """
        Returns the string representation of the input order.

        Returns:
            str: A string representation of the input order.
        """
        return f"Compra de {self.date_created}"


class InputOrderItem(models.Model):
    """
    Represents an item in an input order.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    """ForeignKey: The product associated with the input order item."""

    quantity = models.PositiveIntegerField(default=0)
    """PositiveIntegerField: The quantity of the product in the input order item."""

    inputOrder = models.ForeignKey(InputOrder, on_delete=models.CASCADE)
    """ForeignKey: The input order associated with the item."""

    def getSubtotal(self):
        return round(self.quantity * self.product.price, 2)

    def __str__(self):
        """
        Returns the string representation of the input order item.

        Returns:
            str: A string representation of the input order item.
        """
        return f"{self.product.name} - {self.quantity}"
