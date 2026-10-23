from django.shortcuts import render

# Create your views here.
from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart, CartItem
from products.models import Product

from .models import Order, OrderItem
from .serializers import OrderSerializer


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        # Lock the customer's cart row while checkout runs.
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart = Cart.objects.select_for_update().get(pk=cart.pk)

        cart_items = list(
            CartItem.objects.filter(cart=cart)
            .select_related("product", "product__category")
            .order_by("product_id")
        )

        if not cart_items:
            raise ValidationError({
                "detail": "Your cart is empty. Add products before checkout."
            })

        # Lock products in a consistent order to reduce deadlock risk.
        product_ids = sorted({item.product_id for item in cart_items})

        locked_products = {
            product.pk: product
            for product in Product.objects.select_for_update()
            .filter(pk__in=product_ids)
            .order_by("pk")
        }

        validated_items = []
        total_amount = Decimal("0.00")

        for cart_item in cart_items:
            product = locked_products.get(cart_item.product_id)

            if (
                product is None
                or not product.is_active
                or not product.category.is_active
            ):
                raise ValidationError({
                    "detail": (
                        f"{cart_item.product.name} is no longer available."
                    )
                })

            if cart_item.quantity > product.stock_quantity:
                raise ValidationError({
                    "detail": (
                        f"Insufficient stock for {product.name}. "
                        f"Available quantity: {product.stock_quantity}."
                    )
                })

            unit_price = product.price
            subtotal = unit_price * cart_item.quantity
            total_amount += subtotal

            validated_items.append({
                "product": product,
                "product_name": product.name,
                "sku": product.sku,
                "unit_price": unit_price,
                "quantity": cart_item.quantity,
                "subtotal": subtotal,
            })

        # Create the order only after every cart item has passed validation.
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
        )

        order_items = [
            OrderItem(
                order=order,
                **item_data,
            )
            for item_data in validated_items
        ]

        OrderItem.objects.bulk_create(order_items)

        # Deduct stock only after successful validation.
        for item_data in validated_items:
            product = item_data["product"]
            quantity = item_data["quantity"]

            Product.objects.filter(pk=product.pk).update(
                stock_quantity=F("stock_quantity") - quantity
            )

        # Clear the cart only after the order and stock updates succeed.
        CartItem.objects.filter(cart=cart).delete()

        order = Order.objects.prefetch_related("items").get(pk=order.pk)

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items")
        )


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items")
        )
