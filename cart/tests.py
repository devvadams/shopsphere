from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Category, Product
from cart.models import Cart, CartItem


User = get_user_model()


class CartTests(APITestCase):
    """Automated tests for ShopSphere shopping cart functionality."""

    def setUp(self):
        # Create the primary customer.
        self.user = User.objects.create_user(
            username="cart_customer",
            email="cart@example.com",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=self.user)

        # Create an active category and product.
        self.category = Category.objects.create(
            name="Electronics",
            slug="electronics",
            is_active=True,
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Cart Test Smartphone",
            slug="cart-test-smartphone",
            sku="CART-PHONE-001",
            description="A smartphone for cart testing.",
            price=Decimal("250000.00"),
            stock_quantity=10,
            is_active=True,
        )

        # Create the customer's cart.
        self.cart = Cart.objects.create(user=self.user)

        self.cart_url = "/api/cart/"
        self.items_url = "/api/cart/items/"

    def add_cart_item(self, quantity=1):
        """Create a cart item directly for test setup."""
        return CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=quantity,
        )

    def test_customer_can_retrieve_their_cart(self):
        """An authenticated customer can retrieve their own cart."""
        self.add_cart_item(quantity=2)

        response = self.client.get(self.cart_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_items"], 2)
        self.assertEqual(
            Decimal(str(response.data["total_price"])),
            Decimal("500000.00"),
        )

    def test_customer_can_add_product_to_cart(self):
        """A customer can add an available product to their cart."""
        response = self.client.post(
            self.items_url,
            {
                "product_id": self.product.id,
                "quantity": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        item = CartItem.objects.get(
            cart=self.cart,
            product=self.product,
        )
        self.assertEqual(item.quantity, 2)

    def test_adding_same_product_increments_quantity(self):
        """Adding an existing product increases its cart quantity."""
        first_response = self.client.post(
            self.items_url,
            {
                "product_id": self.product.id,
                "quantity": 2,
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.client.post(
            self.items_url,
            {
                "product_id": self.product.id,
                "quantity": 3,
            },
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        item = CartItem.objects.get(
            cart=self.cart,
            product=self.product,
        )
        self.assertEqual(item.quantity, 5)

        # Only one cart item should exist for this product.
        self.assertEqual(
            CartItem.objects.filter(
                cart=self.cart,
                product=self.product,
            ).count(),
            1,
        )

    def test_customer_can_update_cart_item_quantity(self):
        """A customer can update the quantity of their cart item."""
        item = self.add_cart_item(quantity=2)

        response = self.client.patch(
            f"{self.items_url}{item.id}/",
            {"quantity": 4},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        item.refresh_from_db()
        self.assertEqual(item.quantity, 4)

    def test_update_rejects_quantity_above_available_stock(self):
        """A customer cannot request more items than are in stock."""
        item = self.add_cart_item(quantity=2)

        response = self.client.patch(
            f"{self.items_url}{item.id}/",
            {"quantity": 11},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

    def test_customer_can_remove_cart_item(self):
        """A customer can remove an item from their cart."""
        item = self.add_cart_item(quantity=1)

        response = self.client.delete(
            f"{self.items_url}{item.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            CartItem.objects.filter(id=item.id).exists()
        )

    def test_customer_cannot_access_another_users_cart_item(self):
        """A customer cannot retrieve another customer's cart item."""
        other_user = User.objects.create_user(
            username="other_cart_customer",
            email="other-cart@example.com",
            password="AnotherPassword123!",
        )

        other_cart = Cart.objects.create(user=other_user)

        other_item = CartItem.objects.create(
            cart=other_cart,
            product=self.product,
            quantity=1,
        )

        response = self.client.get(
            f"{self.items_url}{other_item.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        # The other customer's item must remain unchanged.
        other_item.refresh_from_db()
        self.assertEqual(other_item.quantity, 1)