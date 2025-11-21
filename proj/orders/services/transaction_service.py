# TO DO: Implement transaction service
# Due to Sandbox mode, we cannot test the transaction service fully.

# """
# Transaction service for handling Stripe transaction data.
# """
# import stripe
# from stripe import StripeError
# import logging
# from datetime import datetime
# from decimal import Decimal
# from typing import Optional
# from django.conf import settings
# from orders.models import Transaction, Order

# logger = logging.getLogger(__name__)


# def get_stripe_client():
#     """Get configured Stripe client"""
#     stripe.api_key = settings.STRIPE_SECRET_KEY
#     return stripe


# def sync_transaction_from_stripe(payment_intent_id: str, order: Order) -> Optional[Transaction]:
#     """
#     Sync transaction data from Stripe PaymentIntent.
    
#     Args:
#         payment_intent_id: Stripe PaymentIntent ID
#         order: Order instance
        
#     Returns:
#         Transaction instance or None if error
#     """
#     try:
#         stripe_client = get_stripe_client()
#         payment_intent = stripe_client.PaymentIntent.retrieve(
#             payment_intent_id,
#             expand=['charges.data.payment_method']
#         )
        
#         # Get charge data if available
#         charge = None
#         try:
#             # PaymentIntent.charges is a ListObject, need to access .data
#             if hasattr(payment_intent, 'charges') and payment_intent.charges:
#                 charges_list = payment_intent.charges.data if hasattr(payment_intent.charges, 'data') else []
#                 if len(charges_list) > 0:
#                     charge = charges_list[0]
#         except (AttributeError, TypeError) as e:
#             logger.warning(f"Could not access charges for PaymentIntent {payment_intent_id}: {e}")
#             charge = None
        
#         # Extract payment method details
#         payment_method_type = ""
#         payment_method_last4 = ""
#         payment_method_brand = ""
        
#         if charge and hasattr(charge, "payment_method_details"):
#             pm_details = charge.payment_method_details
#             if hasattr(pm_details, "card"):
#                 payment_method_type = "card"
#                 payment_method_last4 = pm_details.card.last4 if hasattr(pm_details.card, "last4") else ""
#                 payment_method_brand = pm_details.card.brand if hasattr(pm_details.card, "brand") else ""
        
#         # Determine transaction type and status
#         transaction_type = "payment"
#         status = payment_intent.status
        
#         # Check for refunds
#         amount_refunded = Decimal(payment_intent.amount_refunded) / 100 if payment_intent.amount_refunded else Decimal("0")
#         if amount_refunded > 0:
#             if amount_refunded >= Decimal(payment_intent.amount) / 100:
#                 status = "refunded"
#             else:
#                 status = "partially_refunded"
        
#         # Create or update transaction
#         transaction, created = Transaction.objects.update_or_create(
#             stripe_payment_intent_id=payment_intent.id,
#             defaults={
#                 "order": order,
#                 "status": status,
#                 "amount": Decimal(payment_intent.amount) / 100,  # Convert from cents
#                 "currency": payment_intent.currency,
#                 "amount_refunded": amount_refunded,
#                 "payment_method_type": payment_method_type,
#                 "payment_method_last4": payment_method_last4,
#                 "payment_method_brand": payment_method_brand,
#                 "stripe_charge_id": charge.id if charge and hasattr(charge, 'id') else None,
#                 "stripe_created_at": datetime.fromtimestamp(payment_intent.created) if payment_intent.created else None,
#                 "receipt_url": charge.receipt_url if charge and hasattr(charge, "receipt_url") else None,
#                 "failure_code": payment_intent.last_payment_error.code if hasattr(payment_intent, "last_payment_error") and payment_intent.last_payment_error else None,
#                 "failure_message": payment_intent.last_payment_error.message if hasattr(payment_intent, "last_payment_error") and payment_intent.last_payment_error else None,
#                 "raw_stripe_data": payment_intent.to_dict(),
#             }
#         )
        
#         if created:
#             logger.info(f"Created transaction {transaction.id} for order {order.id}")
#         else:
#             logger.info(f"Updated transaction {transaction.id} for order {order.id}")
        
#         return transaction
        
#     except StripeError as e:
#         logger.error(f"Stripe error syncing transaction {payment_intent_id}: {e}")
#         return None
#     except Exception as e:
#         logger.error(f"Error syncing transaction {payment_intent_id}: {e}")
#         return None


# def verify_and_update_order_payment_status(order: Order) -> bool:
#     """
#     Verify payment status with Stripe and update order if needed.
    
#     Args:
#         order: Order instance
        
#     Returns:
#         True if payment status was updated, False otherwise
#     """
#     if not order.stripe_payment_intent_id:
#         return False
    
#     try:
#         transaction = sync_transaction_from_stripe(order.stripe_payment_intent_id, order)
        
#         if transaction and transaction.is_successful() and not order.is_paid:
#             order.is_paid = True
#             order.save(update_fields=["is_paid"])
#             logger.info(f"Updated order {order.id} payment status to paid")
#             return True
        
#         return False
        
#     except Exception as e:
#         logger.error(f"Error verifying payment status for order {order.id}: {e}")
#         return False


# def get_transaction_by_payment_intent(payment_intent_id: str) -> Optional[Transaction]:
#     """
#     Get transaction by Stripe PaymentIntent ID.
    
#     Args:
#         payment_intent_id: Stripe PaymentIntent ID
        
#     Returns:
#         Transaction instance or None
#     """
#     try:
#         return Transaction.objects.get(stripe_payment_intent_id=payment_intent_id)
#     except Transaction.DoesNotExist:
#         return None


# def get_order_transactions(order: Order):
#     """
#     Get all transactions for an order.
    
#     Args:
#         order: Order instance
        
#     Returns:
#         QuerySet of Transaction instances
#     """
#     return Transaction.objects.filter(order=order).order_by("-created_at")

