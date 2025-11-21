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
    amount = int(item.price * 100)

    payment_intent = stripe.PaymentIntent.create(
        amount=amount,
        currency='usd',
        metadata={'item_id': item.id, 'item_name': item.name},
        automatic_payment_methods={'enabled': True},
    )

    return JsonResponse({
        'client_secret': payment_intent.client_secret,
        'payment_intent_id': payment_intent.id
    })


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
