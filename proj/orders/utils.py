from django.conf import settings
from decimal import Decimal


def convert_usd_to_eur(usd_amount):
    """Convert USD amount to EUR using the conversion rate from settings"""
    return Decimal(str(usd_amount)) * Decimal(str(settings.USD_TO_EUR_RATE))


def convert_price(amount, from_currency, to_currency):
    """Convert price from one currency to another"""
    if from_currency == to_currency:
        return Decimal(str(amount))
    
    if from_currency == "usd" and to_currency == "eur":
        return convert_usd_to_eur(amount)
    elif from_currency == "eur" and to_currency == "usd":
        # EUR to USD: divide by the rate
        return Decimal(str(amount)) / Decimal(str(settings.USD_TO_EUR_RATE))
    
    return Decimal(str(amount))


