import os

import stripe
from django.urls import reverse
from django.http import HttpRequest

from .models import Payment

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_stripe_session(request, borrowing):
    total_price = borrowing.book.daily_fee
    unit_amount = int(total_price * 100)

    success_url = request.build_absolute_uri(reverse("payments:payment-success"))
    cancel_url = request.build_absolute_uri(reverse("payments:payment-cancel"))

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": unit_amount,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=Payment.TypeChoices.PAYMENT,
        borrowing=borrowing,
        session_id=session.id,
        session_url=session.url,
        money_to_pay=total_price,
    )

    return session.id
