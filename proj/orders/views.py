# orders/views.py
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Order
from .services.stripe_service import create_payment_intent_for_order
from .services.order_service import (
    validate_and_collect_items,
    validate_currency,
    create_order_with_items
)
from .services.order_query_service import (
    get_discounts,
    get_taxes,
    get_order_detail_optimized,
    get_orders_optimized
)
# from .services.transaction_service import verify_and_update_order_payment_status
from items.models import Item


def create_order(request):
    """Display form to create a new order"""
    items = Item.objects.all()
    discounts = get_discounts()
    taxes = get_taxes()
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
        discounts = get_discounts()
        taxes = get_taxes()
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
    try:
        order = get_order_detail_optimized(id)
    except Order.DoesNotExist:
        order = get_object_or_404(Order, pk=id)
    
    # TODO: Transaction service is commented out - payment verification disabled
    # if order.stripe_payment_intent_id and not order.is_paid:
    #     verify_and_update_order_payment_status(order)
    #     order.refresh_from_db()
    
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
    # TODO: Transaction service is commented out - simplified payment success handling
    # from .services.transaction_service import sync_transaction_from_stripe
    
    try:
        order = get_order_detail_optimized(id)
    except Order.DoesNotExist:
        order = get_object_or_404(Order, pk=id)
    
    # Mark order as paid (payment was confirmed client-side)
    if not order.is_paid:
        order.is_paid = True
        order.save(update_fields=["is_paid"])
    
    # TODO: Transaction syncing disabled
    # if order.stripe_payment_intent_id:
    #     sync_transaction_from_stripe(order.stripe_payment_intent_id, order)
    #     verify_and_update_order_payment_status(order)
    #     order.refresh_from_db()
    
    context = {"order": order}
    return render(request, "orders/success.html", context)


def order_cancel(request, id):
    """Handle canceled payment"""
    order = get_object_or_404(Order, pk=id)
    context = {"order": order}
    return render(request, "orders/cancel.html", context)


def order_list(request):
    """Display list of all orders"""
    orders = get_orders_optimized()
    context = {"orders": orders}
    return render(request, "orders/order_list.html", context)