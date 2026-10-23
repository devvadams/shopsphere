from django.test import TestCase

# Create your tests here.

from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product


class ProductAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Electronics",
            slug="electronics",
            is_active=True,
        )

        cls.product = Product.objects.create(
            category=cls.category,
            name="Test Phone",
            slug="test-phone",
            sku="PHONE-001",
            description="A test smartphone",
            price=Decimal("25000.00"),
            stock_quantity=10,
            is_active=True,
        )

    def test_product_list_returns_active_products(self):
        response = self.client.get(reverse("products:product-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["name"],
            "Test Phone",
        )

    def test_product_detail_returns_product(self):
        response = self.client.get(
            reverse(
                "products:product-detail",
                kwargs={"slug": "test-phone"},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["sku"], "PHONE-001")

    def test_inactive_products_are_hidden(self):
        Product.objects.create(
            category=self.category,
            name="Hidden Phone",
            slug="hidden-phone",
            sku="PHONE-002",
            price=Decimal("10000.00"),
            stock_quantity=5,
            is_active=False,
        )

        response = self.client.get(reverse("products:product-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_search_by_name(self):
        response = self.client.get(
            reverse("products:product-list"),
            {"search": "Test Phone"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_category_slug(self):
        response = self.client.get(
            reverse("products:product-list"),
            {"category__slug": "electronics"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_category_list_returns_active_categories(self):
        response = self.client.get(reverse("products:category-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["slug"],
            "electronics",
        )
