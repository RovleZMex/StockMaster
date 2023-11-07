from django.db import models


class Worker(models.Model):
    """
    Represents an employee in the organization.
    """

    name = models.CharField(max_length=255)
    """
    str: The name of the employee.
    """

    employeeNumber = models.IntegerField(unique=True)
    """
    int: The unique employee number.
    """

    workArea = models.CharField(max_length=255)
    """
    str: The work area of the employee.
    """

    def __str__(self):
        """
        Returns the string representation of the employee.

        Returns:
            str: The name of the employee.
        """
        return self.name
