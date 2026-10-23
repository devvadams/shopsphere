
from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(
        source="product.id",
        read_only=True,
    )
    product = ProductSerializer(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product_id",
            "product",
            "quantity",
            "subtotal",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            "id",
            "items",
            "total_items",
            "total_price",
            "created_at",
            "updated_at",
        )

    def get_total_price(self, obj):
        total = sum(
            (item.subtotal for item in obj.items.all()),
            Decimal("0.00"),
        )
        return total

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())


class CartItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, attrs):
        try:
            product = Product.objects.select_related("category").get(
                pk=attrs["product_id"],
                is_active=True,
                category__is_active=True,
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                "product_id": "This product is unavailable."
            })

        requested_quantity = attrs["quantity"]
        user = self.context["request"].user

        existing_item = CartItem.objects.filter(
            cart__user=user,
            product=product,
        ).first()

        current_quantity = (
            existing_item.quantity if existing_item else 0
        )

        if current_quantity + requested_quantity > product.stock_quantity:
            raise serializers.ValidationError({
                "quantity": (
                    f"Only {product.stock_quantity} unit(s) are "
                    "currently available."
                )
            })

        attrs["product"] = product
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        product = validated_data["product"]
        quantity = validated_data["quantity"]
        user = self.context["request"].user

        cart, _ = Cart.objects.get_or_create(user=user)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )

        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity", "updated_at"])

        return item


class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ("quantity",)

    def validate_quantity(self, value):
        if value > self.instance.product.stock_quantity:
            raise serializers.ValidationError(
                "The requested quantity exceeds available stock."
            )
        return value
