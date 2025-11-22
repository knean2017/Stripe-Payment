import stripe
from django.conf import settings
from decimal import Decimal
from typing import Dict


def get_stripe_client():
    """Get configured Stripe client"""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def create_payment_intent_for_item(item, currency: str = "usd") -> Dict[str, str]:
    """
    Create PaymentIntent for an item
    
    Args:
        item: Item instance
        currency: Currency code ('usd' or 'eur')
        
    Returns:
        Dict with client_secret and payment_intent_id
    """
    stripe_client = get_stripe_client()
    
    # Validate currency
    if currency not in ["usd", "eur"]:
        currency = "usd"
    
    # Convert price if EUR is selected
    if currency == "eur":
        converted_price = Decimal(str(item.price)) * Decimal(str(settings.USD_TO_EUR_RATE))
        amount = int(converted_price * 100)
    else:
        amount = int(item.price * 100)

    payment_intent = stripe_client.PaymentIntent.create(
        amount=amount,
        currency=currency,
        metadata={"item_id": item.id, "item_name": item.name},
        automatic_payment_methods={"enabled": True},
    )

    return {
        "client_secret": payment_intent.client_secret,
        "payment_intent_id": payment_intent.id
    }

