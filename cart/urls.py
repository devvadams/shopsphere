
from django.urls import path

from .views import (
    CartItemDetailView,
    CartItemListCreateView,
    CartView,
)

app_name = "cart"

urlpatterns = [
    path("", CartView.as_view(), name="cart-detail"),
    path("items/", CartItemListCreateView.as_view(), name="cart-items"),
    path(
        "items/<int:pk>/",
        CartItemDetailView.as_view(),
        name="cart-item-detail",
    ),
]
