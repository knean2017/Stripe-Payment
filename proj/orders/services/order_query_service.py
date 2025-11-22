"""
Order query service for optimized database queries.
"""
from django.db.models import QuerySet
from orders.models import Order, Discount, Tax


def get_orders_optimized() -> QuerySet[Order]:
    """
    Get all orders with optimized queries.
    
    Returns:
        QuerySet with select_related and prefetch_related
    """
    return Order.objects.select_related(
        "discount",
        "tax"
    ).prefetch_related(
        "order_items__item",
    ).order_by("-created_at")


def get_order_detail_optimized(order_id: int) -> Order:
    """
    Get order by ID with optimized queries.
    
    Args:
        order_id: Order ID
        
    Returns:
        Order instance
        
    Raises:
        Order.DoesNotExist: If order not found
    """
    return Order.objects.select_related(
        "discount",
        "tax"
    ).prefetch_related(
        "order_items__item",

    ).get(pk=order_id)


def get_discounts() -> QuerySet[Discount]:
    """Get all discounts"""
    return Discount.objects.all()


def get_taxes() -> QuerySet[Tax]:
    """Get all taxes"""
    return Tax.objects.all()

