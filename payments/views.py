import os

from django.http import HttpResponse
from dotenv import load_dotenv

import stripe
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment
from payments.permissions import IsAdminOrOwnerUser
from payments.serializers import PaymentSerializer

load_dotenv()


class PaymentListAPIView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        else:
            return Payment.objects.filter(user=user)


class PaymentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (IsAdminOrOwnerUser,)


stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class CreateCheckoutSessionView(APIView):
    def post(self, request, *args, **kwargs):
        payment_id = request.data.get("payment_id")
        payment = get_object_or_404(Payment, id=payment_id)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Library Payment",
                        },
                        "unit_amount": int(payment.money_to_pay * 100),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://localhost:8000/payments/success/",
            cancel_url="http://localhost:8000/payments/cancel/",
        )

        payment.session_id = session.id
        payment.session_url = session.url
        payment.save()

        return Response({"id": session.id}, status=status.HTTP_200_OK)


class PaymentSuccessView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Payment was successful.")


class PaymentCancelView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Payment was cancelled.")
