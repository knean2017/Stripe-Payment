"""
Discount model for orders.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    CURRENCY_CHOICES = [
        ("usd", "USD"),
        ("eur", "EUR"),
    ]
    
    name = models.CharField(max_length=255)
    discount_type = models.CharField(
        max_length=20, 
        choices=DISCOUNT_TYPE_CHOICES, 
        default="percentage"
    )
    value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="usd"
    )
    
    def __str__(self):
        if self.discount_type == "percentage":
            return f"{self.name} ({self.value}%)"
        return f"{self.name} ({self.value} {self.currency.upper()})"
    
    def calculate_discount(self, subtotal):
        """Calculate discount amount based on subtotal"""
        if self.discount_type == "percentage":
            return subtotal * (self.value / 100)
        return self.value

