from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from .models import Item


def item_list(request):
    """Display list of all items"""
    items = Item.objects.all()
    context = {
        "items": items,
        "usd_to_eur_rate": settings.USD_TO_EUR_RATE,
    }
    return render(request, "items/item_list.html", context)


def buy(request, id):
    """Create an order with the selected item and redirect to order detail"""
    # Lazy import to avoid circular import
    from orders.models import Order, OrderItem
    from orders.utils import convert_price
    
    item = get_object_or_404(Item, pk=id)
    
    # Get currency from request (default to USD)
    currency = request.GET.get("currency", "usd")
    if currency not in ["usd", "eur"]:
        currency = "usd"
    
    # Create order with this single item (quantity 1)
    order = Order.objects.create(currency=currency)
    
    # Convert price if EUR is selected
    if currency == "eur":
        converted_price = convert_price(item.price, "usd", "eur")
    else:
        converted_price = item.price
    
    # Create order item
    OrderItem.objects.create(
        order=order,
        item=item,
        quantity=1,
        price_at_purchase=converted_price
    )
    
    # Redirect to order detail page
    return redirect("order_detail", id=order.id)


def item_detail(request, id):
    item = get_object_or_404(Item, pk=id)
    context = {
        "item": item,
        "usd_to_eur_rate": settings.USD_TO_EUR_RATE,
    }
    return render(request, "items/item_detail.html", context)


def success(request):
    return render(request, "items/success.html")


def cancel(request):
    return render(request, "items/cancel.html")
