# orders/views.py
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Order, Discount, Tax
from .services.stripe_service import create_payment_intent_for_order
from .services.order_service import (
    validate_and_collect_items,
    validate_currency,
    create_order_with_items
)
from items.models import Item


def create_order(request):
    """Display form to create a new order"""
    items = Item.objects.all()
    discounts = Discount.objects.all()
    taxes = Tax.objects.all()
    context = {
        "items": items,
        "discounts": discounts,
        "taxes": taxes,
        "selected_currency": None,
        "usd_to_eur_rate": settings.USD_TO_EUR_RATE,
    }
    return render(request, "orders/create_order.html", context)


@require_http_methods(["POST"])
def add_to_order(request):
    """Add items to an order and create it"""
    selected_currency = validate_currency(request.POST.get("currency", "usd"))
    selected_items = validate_and_collect_items(request.POST)
    
    # Check if at least one item is selected
    if not selected_items:
        messages.error(request, "Please select at least one item to create an order.")
        items = Item.objects.all()
        discounts = Discount.objects.all()
        taxes = Tax.objects.all()
        context = {
            "items": items,
            "discounts": discounts,
            "taxes": taxes,
            "selected_currency": selected_currency,
            "usd_to_eur_rate": settings.USD_TO_EUR_RATE,
        }
        return render(request, "orders/create_order.html", context)
    
    # Create order with items using service
    discount_id = request.POST.get("discount")
    tax_id = request.POST.get("tax")
    order = create_order_with_items(
        selected_currency=selected_currency,
        selected_items=selected_items,
        discount_id=discount_id,
        tax_id=tax_id
    )
    
    return redirect("order_detail", id=order.id)


def order_detail(request, id):
    """Display order details"""
    order = get_object_or_404(Order, pk=id)
    context = {
        "order": order,
        "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, "orders/order_detail.html", context)


def buy_order(request, id):
    """Create Stripe PaymentIntent for the entire order"""
    order = get_object_or_404(Order, pk=id)
    
    try:
        result = create_payment_intent_for_order(order)
        return JsonResponse(result)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)


def order_success(request, id):
    """Handle successful payment"""
    order = get_object_or_404(Order, pk=id)
    order.is_paid = True
    order.save()
    
    context = {"order": order}
    return render(request, "orders/success.html", context)


def order_cancel(request, id):
    """Handle canceled payment"""
    order = get_object_or_404(Order, pk=id)
    context = {"order": order}
    return render(request, "orders/cancel.html", context)


def order_list(request):
    """Display list of all orders"""
    orders = Order.objects.all().order_by("-created_at")
    context = {"orders": orders}
    return render(request, "orders/order_list.html", context)