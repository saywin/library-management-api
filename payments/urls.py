from django.urls import path
from .views import (
    PaymentListAPIView,
    PaymentDetailAPIView,
    CreateCheckoutSessionView,
    PaymentSuccessView,
    PaymentCancelView,
)

urlpatterns = [
    path("", PaymentListAPIView.as_view(), name="payment-list"),
    path("<int:pk>/", PaymentDetailAPIView.as_view(), name="payment-detail"),
    path(
        "create-checkout-session/",
        CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]

app_name = "payments"
