from django.db import models
from simple_history.models import HistoricalRecords


class Product(models.Model):
    """
    Represents a product in the inventory.
    """

    name = models.CharField(max_length=255)
    """
    str: The name of the product.
    """

    SKU = models.CharField(max_length=255, unique=True)
    """
    str: The stock keeping unit of the product.
    """

    price = models.FloatField(default=0.0)
    """
    float: The price of the product.
    """

    quantity = models.PositiveIntegerField(default=0)
    """
    int: The current stock quantity of the product.
    """

    image = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True)
    """
    str: The image associated with the product.
    """

    threshold = models.PositiveIntegerField(default=0)
    """
    int: The threshold indicating low stock.
    """

    category = models.CharField(max_length=255, choices=[
        ('ELE', 'Eléctrico'),
        ('PLU', 'Plomería'),
        ('OFF', 'Oficina'),
        ('CLE', 'Limpieza')
    ])
    """
    str: The category of the product.
    """

    isExternal = models.BooleanField(default=False)
    """
    bool: Indicates if the product is acquired from outside the institution.
    """

    history = HistoricalRecords()
    """
    :meta private:
    HistoricalRecords: Used to manage historical modifications of the product.
    """

    def isLowStock(self):
        """
        Check if the product is in low stock.

        Returns:
            bool: True if the product is in low stock, False otherwise.
        """
        return self.quantity <= self.threshold

    def __str__(self):
        """
        Returns the string representation of the product.

        Returns:
            str: The name of the product.
        """
        return self.name
