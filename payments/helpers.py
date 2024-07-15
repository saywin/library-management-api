import os

import stripe
from django.conf import settings
from django.urls import reverse


from .models import Payment

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_stripe_session(borrowing):
    total_price = borrowing.book.daily_fee
    unit_amount = int(total_price * 100)

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
        success_url=settings.BASE_URL + reverse("payments:payment-success"),
        cancel_url=settings.BASE_URL + reverse("payments:payment-cancel"),
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
