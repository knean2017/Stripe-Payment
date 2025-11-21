# TO DO: Implement transaction model
# Due to Sandbox mode, we cannot test the transaction model fully.

# """
# Transaction model for tracking Stripe payments.
# """
# from django.db import models
# from decimal import Decimal


# class Transaction(models.Model):
#     STATUS_CHOICES = [
#         ("pending", "Pending"),
#         ("succeeded", "Succeeded"),
#         ("failed", "Failed"),
#         ("canceled", "Canceled"),
#         ("refunded", "Refunded"),
#         ("partially_refunded", "Partially Refunded"),
#         ("requires_action", "Requires Action"),
#         ("processing", "Processing"),
#     ]
    
#     TRANSACTION_TYPES = [
#         ("payment", "Payment"),
#         ("refund", "Refund"),
#         ("chargeback", "Chargeback"),
#     ]
    
#     # Relations
#     order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="transactions")
    
#     # Stripe identifiers
#     stripe_payment_intent_id = models.CharField(max_length=255, unique=True, db_index=True)
#     stripe_charge_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    
#     # Transaction details
#     transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default="payment")
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     currency = models.CharField(max_length=3, default="usd")
#     amount_refunded = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
#     # Payment method info
#     payment_method_type = models.CharField(max_length=50, blank=True)  # card, bank_account, etc.
#     payment_method_last4 = models.CharField(max_length=4, blank=True)  # Last 4 digits
#     payment_method_brand = models.CharField(max_length=50, blank=True)  # visa, mastercard, etc.
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     stripe_created_at = models.DateTimeField(null=True, blank=True)  # From Stripe
    
#     # Additional data
#     failure_code = models.CharField(max_length=100, blank=True, null=True)
#     failure_message = models.TextField(blank=True, null=True)
#     receipt_url = models.URLField(blank=True, null=True)
#     raw_stripe_data = models.JSONField(default=dict, blank=True)  # Store full Stripe response
    
#     class Meta:
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["stripe_payment_intent_id"]),
#             models.Index(fields=["order", "-created_at"]),
#             models.Index(fields=["status", "-created_at"]),
#         ]
    
#     def __str__(self):
#         return f"Transaction {self.stripe_payment_intent_id[:20]}... - {self.status}"
    
#     def is_successful(self):
#         """Check if transaction was successful"""
#         return self.status == "succeeded"
    
#     def get_net_amount(self):
#         """Get amount after refunds"""
#         return self.amount - self.amount_refunded
    
#     def is_refunded(self):
#         """Check if transaction is fully or partially refunded"""
#         return self.status in ["refunded", "partially_refunded"]

