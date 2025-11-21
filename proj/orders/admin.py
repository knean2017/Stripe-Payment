# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem, Discount, Tax


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("name", "discount_type", "value", "currency")
    list_filter = ("discount_type",)


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("name", "percentage")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ("get_subtotal",)
    
    def get_subtotal(self, obj):
        if obj.id:
            return f"${obj.get_subtotal():.2f}"
        return "-"
    get_subtotal.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "currency", "discount", "tax", "is_paid", "display_total")
    list_filter = ("is_paid", "currency", "created_at", "discount", "tax")
    readonly_fields = ("created_at", "updated_at", "stripe_session_id", "display_subtotal", "display_discount", "display_tax", "display_total")
    inlines = [OrderItemInline]
    
    def display_subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    display_subtotal.short_description = "Subtotal"
    
    def display_discount(self, obj):
        return f"-${obj.get_discount_amount():.2f}"
    display_discount.short_description = "Discount"
    
    def display_tax(self, obj):
        return f"${obj.get_tax_amount():.2f}"
    display_tax.short_description = "Tax"
    
    def display_total(self, obj):
        return f"${obj.get_total():.2f}"
    display_total.short_description = "Total"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "item", "quantity", "price_at_purchase", "display_subtotal")
    list_filter = ("order",)
    readonly_fields = ("display_subtotal",)
    
    def display_subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    display_subtotal.short_description = "Subtotal"