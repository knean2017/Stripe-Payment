from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import Item
import stripe


def item_list(request):
    """Display list of all items"""
    items = Item.objects.all()
    context = {'items': items}
    return render(request, 'items/item_list.html', context)


def buy(request, id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    item = get_object_or_404(Item, pk=id)
    unit_amount = int(item.price * 100)

    session = stripe.checkout.Session.create(
        mode='payment',
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': item.name},
                'unit_amount': unit_amount,
            },
            'quantity': 1,
        }],
        success_url=request.build_absolute_uri(reverse('item_success')),
        cancel_url=request.build_absolute_uri(reverse('item_cancel')),
    )

    return JsonResponse({'id': session.id})


def item_detail(request, id):
    item = get_object_or_404(Item, pk=id)
    context = {
        'item': item,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'items/item_detail.html', context)


def success(request):
    return render(request, 'items/success.html')


def cancel(request):
    return render(request, 'items/cancel.html')
