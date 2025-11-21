import stripe
from stripe import InvalidRequestError
from django.conf import settings
from typing import Dict, Optional


def get_stripe_client():
    """Get configured Stripe client"""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def create_payment_intent_for_order(order) -> Dict[str, str]:
    """
    Create or retrieve PaymentIntent for an order
    
    Args:
        order: Order instance
        
    Returns:
        Dict with client_secret and payment_intent_id
        
    Raises:
        ValueError: If order has no items
    """
    if not order.order_items.exists():
        raise ValueError("Order has no items")
    
    stripe_client = get_stripe_client()
    total_amount = order.get_total_cents()
    
    # Try to retrieve existing PaymentIntent
    if order.stripe_payment_intent_id:
        try:
            payment_intent = stripe_client.PaymentIntent.retrieve(
                order.stripe_payment_intent_id
            )
            # Update amount if it changed
            if payment_intent.amount != total_amount:
                payment_intent = stripe_client.PaymentIntent.modify(
                    order.stripe_payment_intent_id,
                    amount=total_amount,
                )
            return {
                "client_secret": payment_intent.client_secret,
                "payment_intent_id": payment_intent.id
            }
        except InvalidRequestError:
            # PaymentIntent doesn't exist, create new one
            pass
    
    # Create new PaymentIntent
    payment_intent = stripe_client.PaymentIntent.create(
        amount=total_amount,
        currency=order.currency,
        metadata={"order_id": order.id},
        automatic_payment_methods={"enabled": True},
    )
    
    # Save PaymentIntent ID to order
    order.stripe_payment_intent_id = payment_intent.id
    order.save(update_fields=["stripe_payment_intent_id"])
    
    return {
        "client_secret": payment_intent.client_secret,
        "payment_intent_id": payment_intent.id
    }

