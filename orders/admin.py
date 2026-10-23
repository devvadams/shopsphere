# Register your models here.
from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "product_name",
        "sku",
        "unit_price",
        "quantity",
        "subtotal",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "payment_status",
        "total_amount",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_status",
        "created_at",
    )
    search_fields = (
        "user__username",
        "user__email",
    )
    readonly_fields = (
        "user",
        "total_amount",
        "created_at",
        "updated_at",
    )
    inlines = [OrderItemInline]