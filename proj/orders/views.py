# orders/views.py
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Order, OrderItem, Discount, Tax
from .utils import convert_price
from items.models import Item
import stripe


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
    """Create Stripe checkout session for the entire order"""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    order = get_object_or_404(Order, pk=id)
    
    # Ensure order has items
    if not order.order_items.exists():
        return JsonResponse({'error': 'Order has no items'}, status=400)
    
    # Add tax if present - using automatic tax display
    if order.tax:
        # Add tax as a line item to show it clearly
        tax_rate = stripe.TaxRate.create(
            display_name=order.tax.name,
            percentage=float(order.tax.percentage),
            inclusive=False,
        )
        tax_rate_id = tax_rate.id
    else:
        tax_rate_id = None

    # Build line items for Stripe
    line_items = []
    for order_item in order.order_items.all():
        item_data = {
            'price_data': {
                'currency': order.currency,
                'product_data': {
                    'name': order_item.item.name,
                    'description': order_item.item.description,
                },
                'unit_amount': int(order_item.price_at_purchase * 100),
            },
            'quantity': order_item.quantity,
        }
        if tax_rate_id:
            item_data['tax_rates'] = [tax_rate_id]
        line_items.append(item_data)
    
    # Prepare session parameters
    session_params = {
        'mode': 'payment',
        'line_items': line_items,
        'success_url': request.build_absolute_uri(reverse('order_success', kwargs={'id': order.id})),
        'cancel_url': request.build_absolute_uri(reverse('order_cancel', kwargs={'id': order.id})),
        'metadata': {'order_id': order.id},
    }
    
    # Add discount if present
    if order.discount:
        if order.discount.discount_type == 'percentage':
            # Create a coupon for percentage discount
            coupon = stripe.Coupon.create(
                percent_off=float(order.discount.value),
                duration='once',
                name=order.discount.name,
            )
            session_params['discounts'] = [{'coupon': coupon.id}]
        else:
            # For fixed amount discount, create a coupon
            coupon = stripe.Coupon.create(
                amount_off=int(order.discount.value * 100),
                currency=order.currency,
                duration='once',
                name=order.discount.name,
            )
            session_params['discounts'] = [{'coupon': coupon.id}]
    
    
    # Create Stripe checkout session
    session = stripe.checkout.Session.create(**session_params)
    
    # Save session ID to order
    order.stripe_session_id = session.id
    order.save()
    
    return JsonResponse({'id': session.id})


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