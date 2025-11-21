from typing import List, Tuple, Optional
from items.models import Item
from orders.models import Order, OrderItem, Discount, Tax
from orders.utils import convert_price


def validate_and_collect_items(post_data: dict) -> List[Tuple[Item, int]]:
    """
    Validate and collect items from POST data
    
    Args:
        post_data: Django request.POST dict
        
    Returns:
        List of tuples (item, quantity)
    """
    selected_items = []
    for key, value in post_data.items():
        if key.startswith("quantity_"):
            item_id = key.split("_")[1]
            quantity = int(value)
            
            if quantity > 0:
                try:
                    item = Item.objects.get(pk=item_id)
                    selected_items.append((item, quantity))
                except Item.DoesNotExist:
                    pass
    
    return selected_items


def validate_currency(currency: str) -> str:
    """
    Validate currency value
    
    Args:
        currency: Currency string
        
    Returns:
        Valid currency ('usd' or 'eur')
    """
    if currency not in ["usd", "eur"]:
        return "usd"
    return currency


def create_order_with_items(
    selected_currency: str,
    selected_items: List[Tuple[Item, int]],
    discount_id: Optional[str] = None,
    tax_id: Optional[str] = None
) -> Order:
    """
    Create order with items, discount, and tax
    
    Args:
        selected_currency: Currency for the order
        selected_items: List of (item, quantity) tuples
        discount_id: Optional discount ID
        tax_id: Optional tax ID
        
    Returns:
        Created Order instance
    """
    order = Order.objects.create(currency=selected_currency)
    
    # Add discount if provided
    if discount_id:
        try:
            order.discount = Discount.objects.get(pk=discount_id)
        except Discount.DoesNotExist:
            pass
    
    # Add tax if provided
    if tax_id:
        try:
            order.tax = Tax.objects.get(pk=tax_id)
        except Tax.DoesNotExist:
            pass
    
    order.save()
    
    # Create order items with converted prices if needed
    for item, quantity in selected_items:
        if selected_currency == "eur":
            converted_price = convert_price(item.price, "usd", "eur")
        else:
            converted_price = item.price
        
        OrderItem.objects.create(
            order=order,
            item=item,
            quantity=quantity,
            price_at_purchase=converted_price
        )
    
    return order

