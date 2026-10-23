
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True).order_by("name")


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = {
        "category__slug": ["exact"],
        "price": ["exact", "gte", "lte"],
    }

    search_fields = ["name", "description", "sku", "category__name"]

    ordering_fields = ["name", "price", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Product.objects.filter(
                is_active=True,
                category__is_active=True,
            )
            .select_related("category")
        )


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True,
            category__is_active=True,
        ).select_related("category")
