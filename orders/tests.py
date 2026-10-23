from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Category, Product
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem


User = get_user_model()


class CheckoutTests(APITestCase):
    """Automated tests for ShopSphere checkout and order access."""

    def setUp(self):
        # Create a customer for each test.
        self.user = User.objects.create_user(
            username="checkout_customer",
            email="checkout@example.com",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=self.user)

        # Create an active product category.
        self.category = Category.objects.create(
            name="Electronics",
            slug="electronics",
            is_active=True,
        )

        # Create a product with known price and stock.
        self.product = Product.objects.create(
            category=self.category,
            name="Test Smartphone",
            slug="test-smartphone",
            sku="PHONE-TEST-001",
            description="A smartphone for checkout testing.",
            price=Decimal("250000.00"),
            stock_quantity=10,
            is_active=True,
        )

        # Create the customer's cart.
        self.cart = Cart.objects.create(user=self.user)

        self.checkout_url = "/api/orders/checkout/"
        self.cart_items_url = "/api/cart/items/"

    def add_cart_item(self, quantity=1):
        """Add an item directly to the cart for test setup."""
        return CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=quantity,
        )

    def test_successful_checkout_creates_order(self):
        """A customer with a valid cart can place an order."""
        self.add_cart_item(quantity=2)

        response = self.client.post(self.checkout_url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)

        order = Order.objects.get(user=self.user)

        self.assertEqual(
            order.total_amount,
            Decimal("500000.00"),
        )
        self.assertEqual(order.items.count(), 1)

    def test_checkout_rejects_empty_cart(self):
        """Checkout must not create an order for an empty cart."""
        response = self.client.post(self.checkout_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Order.objects.filter(user=self.user).exists())

    def test_checkout_rejects_insufficient_stock(self):
        """Insufficient inventory must prevent checkout."""
        # Insert directly so the cart can contain more than available stock.
        self.product.stock_quantity = 2
        self.product.save(update_fields=["stock_quantity"])

        self.add_cart_item(quantity=3)

        response = self.client.post(self.checkout_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Order.objects.filter(user=self.user).exists())

        # Failed checkout must not reduce stock.
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 2)

        # The cart item should remain available for correction.
        self.assertTrue(
            CartItem.objects.filter(cart=self.cart).exists()
        )

    def test_checkout_deducts_stock(self):
        """Successful checkout reduces inventory by the purchased quantity."""
        self.add_cart_item(quantity=3)

        response = self.client.post(self.checkout_url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 7)

    def test_checkout_clears_cart(self):
        """Successful checkout removes purchased items from the cart."""
        self.add_cart_item(quantity=2)

        response = self.client.post(self.checkout_url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(
            CartItem.objects.filter(cart=self.cart).exists()
        )

    def test_order_preserves_purchase_price(self):
        """Order items retain the price used at checkout."""
        self.add_cart_item(quantity=2)

        response = self.client.post(self.checkout_url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(user=self.user)
        order_item = order.items.get()

        self.assertEqual(order_item.unit_price, Decimal("250000.00"))
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.subtotal, Decimal("500000.00"))

        # A later product price change must not alter the historical order.
        self.product.price = Decimal("300000.00")
        self.product.save(update_fields=["price"])

        order_item.refresh_from_db()
        self.assertEqual(order_item.unit_price, Decimal("250000.00"))
        self.assertEqual(order_item.subtotal, Decimal("500000.00"))

    def test_customer_cannot_access_another_users_order(self):
        """A customer cannot retrieve another customer's order."""
        order = Order.objects.create(
            user=self.user,
            status=Order.Status.PENDING,
            payment_status=Order.PaymentStatus.UNPAID,
            total_amount=Decimal("250000.00"),
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            sku=self.product.sku,
            unit_price=self.product.price,
            quantity=1,
            subtotal=self.product.price,
        )

        other_user = User.objects.create_user(
            username="another_customer",
            email="another@example.com",
            password="AnotherPassword123!",
        )

        order.user = other_user
        order.save(update_fields=["user"])

        response = self.client.get(f"/api/orders/{order.pk}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
