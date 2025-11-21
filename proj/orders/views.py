# orders/views.py
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem, Discount, Tax
from .utils import convert_price
from items.models import Item
import stripe
import json


def create_order(request):
    """Display form to create a new order"""
    items = Item.objects.all()
    discounts = Discount.objects.all()
    taxes = Tax.objects.all()
    context = {
        'items': items,
        'discounts': discounts,
        'taxes': taxes,
        'selected_currency': None,
        'usd_to_eur_rate': settings.USD_TO_EUR_RATE,
    }
    return render(request, 'orders/create_order.html', context)


@require_http_methods(["POST"])
def add_to_order(request):
    """Add items to an order and create it"""
    # Get selected currency from form
    selected_currency = request.POST.get('currency', 'usd')
    if selected_currency not in ['usd', 'eur']:
        selected_currency = 'usd'
    
    # Collect items
    selected_items = []
    for key, value in request.POST.items():
        if key.startswith('quantity_'):
            item_id = key.split('_')[1]
            quantity = int(value)
            
            if quantity > 0:
                item = get_object_or_404(Item, pk=item_id)
                selected_items.append((item, quantity))
    
    # Check if at least one item is selected
    if not selected_items:
        messages.error(request, 'Please select at least one item to create an order.')
        items = Item.objects.all()
        discounts = Discount.objects.all()
        taxes = Tax.objects.all()
        context = {
            'items': items,
            'discounts': discounts,
            'taxes': taxes,
            'selected_currency': selected_currency,
            'usd_to_eur_rate': settings.USD_TO_EUR_RATE,
        }
        return render(request, 'orders/create_order.html', context)
    
    # Create order with selected currency
    order = Order.objects.create(currency=selected_currency)
    
    # Add discount if selected
    discount_id = request.POST.get('discount')
    if discount_id:
        order.discount = get_object_or_404(Discount, pk=discount_id)
    
    # Add tax if selected
    tax_id = request.POST.get('tax')
    if tax_id:
        order.tax = get_object_or_404(Tax, pk=tax_id)
    
    order.save()
    
    # Create order items with converted prices if needed
    for item, quantity in selected_items:
        # Items are stored in USD, convert to EUR if order currency is EUR
        if selected_currency == 'eur':
            converted_price = convert_price(item.price, 'usd', 'eur')
        else:
            converted_price = item.price
        
        OrderItem.objects.create(
            order=order,
            item=item,
            quantity=quantity,
            price_at_purchase=converted_price
        )
    
    # Redirect to order detail page
    return redirect('order_detail', id=order.id)


def order_detail(request, id):
    """Display order details"""
    order = get_object_or_404(Order, pk=id)
    context = {
        'order': order,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'orders/order_detail.html', context)


def buy_order(request, id):
    """Create Stripe PaymentIntent for the entire order"""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    order = get_object_or_404(Order, pk=id)
    
    # Ensure order has items
    if not order.order_items.exists():
        return JsonResponse({'error': 'Order has no items'}, status=400)
    
    # Calculate total amount (already includes discount and tax)
    total_amount = order.get_total_cents()
    
    # Create or retrieve PaymentIntent
    if order.stripe_payment_intent_id:
        try:
            payment_intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent_id)
            # Update amount if it changed
            if payment_intent.amount != total_amount:
                payment_intent = stripe.PaymentIntent.modify(
                    order.stripe_payment_intent_id,
                    amount=total_amount,
                )
        except stripe.error.InvalidRequestError:
            # PaymentIntent doesn't exist, create new one
            payment_intent = None
    else:
        payment_intent = None
    
    if not payment_intent:
        # Create new PaymentIntent
        payment_intent = stripe.PaymentIntent.create(
            amount=total_amount,
            currency=order.currency,
            metadata={'order_id': order.id},
            automatic_payment_methods={'enabled': True},
        )
        order.stripe_payment_intent_id = payment_intent.id
        order.save()
    
    return JsonResponse({
        'client_secret': payment_intent.client_secret,
        'payment_intent_id': payment_intent.id
    })


def order_success(request, id):
    """Handle successful payment"""
    order = get_object_or_404(Order, pk=id)
    order.is_paid = True
    order.save()
    
    context = {'order': order}
    return render(request, 'orders/success.html', context)


def order_cancel(request, id):
    """Handle canceled payment"""
    order = get_object_or_404(Order, pk=id)
    context = {'order': order}
    return render(request, 'orders/cancel.html', context)


def order_list(request):
    """Display list of all orders"""
    orders = Order.objects.all().order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'orders/order_list.html', context)


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        payment_intent_id = payment_intent['id']
        
        # Find order by payment_intent_id
        try:
            order = Order.objects.get(stripe_payment_intent_id=payment_intent_id)
            if not order.is_paid:
                order.is_paid = True
                order.save()
        except Order.DoesNotExist:
            pass
    
    return HttpResponse(status=200)