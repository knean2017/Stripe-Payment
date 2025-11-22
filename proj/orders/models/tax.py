"""
Tax model for orders.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Tax(models.Model):
    name = models.CharField(max_length=255)
    percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
            MaxValueValidator(Decimal("100.00"))
        ]
    )
    
    def __str__(self):
        return f"{self.name} ({self.percentage}%)"
    
    def calculate_tax(self, amount):
        """Calculate tax amount based on given amount"""
        return amount * (self.percentage / 100)

