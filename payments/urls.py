from django.urls import path
from rest_framework.reverse import reverse_lazy

from .views import (
    PaymentListAPIView,
    PaymentDetailAPIView,
    CreateCheckoutSessionView,
    StripePaymentSuccessAPIView,
    StripePaymentCancelAPIView,
)

urlpatterns = [
    path("", PaymentListAPIView.as_view(), name="payment-list"),
    path("<int:pk>/", PaymentDetailAPIView.as_view(), name="payment-detail"),
    path(
        "create-checkout-session/",
        CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("success/", StripePaymentSuccessAPIView.as_view(), name="payment-success"),
    path("cancel/", StripePaymentCancelAPIView.as_view(), name="payment-cancel"),
]

app_name = "payments"
