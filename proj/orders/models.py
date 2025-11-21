# orders/models.py
from random import choices
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from items.models import Item
from decimal import Decimal


class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    CURRENCY_CHOICES = [
        ('usd', 'USD'),
        ('eur', 'EUR'),
    ]
    
    name = models.CharField(max_length=255)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='usd')  # Only for fixed discounts
    
    def __str__(self):
        if self.discount_type == 'percentage':
            return f"{self.name} ({self.value}%)"
        return f"{self.name} ({self.value} {self.currency.upper()})"
    
    def calculate_discount(self, subtotal):
        """Calculate discount amount based on subtotal"""
        if self.discount_type == 'percentage':
            return subtotal * (self.value / 100)
        return self.value


class Tax(models.Model):
    name = models.CharField(max_length=255)
    percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100.00'))]
    )
    
    def __str__(self):
        return f"{self.name} ({self.percentage}%)"
    
    def calculate_tax(self, amount):
        """Calculate tax amount based on given amount"""
        return amount * (self.percentage / 100)


class Order(models.Model):
    CURRENCY_CHOICES = [
        ('usd', 'USD'),
        ('eur', 'EUR'),
    ]
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='usd')
    is_paid = models.BooleanField(default=False)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    def __str__(self):
        return f"Order #{self.id} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def get_subtotal(self):
        """Calculate subtotal (before discount and tax)"""
        return sum(order_item.get_subtotal() for order_item in self.order_items.all())
    
    def get_discount_amount(self):
        """Calculate discount amount"""
        if self.discount:
            return self.discount.calculate_discount(self.get_subtotal())
        return Decimal('0.00')
    
    def get_amount_after_discount(self):
        """Calculate amount after discount but before tax"""
        return self.get_subtotal() - self.get_discount_amount()
    
    def get_tax_amount(self):
        """Calculate tax amount on discounted total"""
        if self.tax:
            return self.tax.calculate_tax(self.get_amount_after_discount())
        return Decimal('0.00')
    
    def get_total(self):
        """Calculate final total (subtotal - discount + tax)"""
        return self.get_amount_after_discount() + self.get_tax_amount()
    
    def get_total_cents(self):
        """Get total in cents for Stripe"""
        return int(self.get_total() * 100)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ('order', 'item')
    
    def __str__(self):
        return f"{self.quantity}x {self.item.name} in Order #{self.order.id}"
    
    def get_subtotal(self):
        """Calculate subtotal for this order item"""
        return self.price_at_purchase * self.quantity
    
    def save(self, *args, **kwargs):
        # Store the item's price at the time of purchase
        if not self.price_at_purchase:
            self.price_at_purchase = self.item.price
        super().save(*args, **kwargs)