from datetime import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from payments.helpers import create_stripe_session
from payments.serializers import PaymentSerializer
from users.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.SlugRelatedField(
        read_only=True,
        slug_field="title",
    )


class BorrowingRetrieveSerializer(BorrowingSerializer):
    book = BookSerializer()
    user = UserSerializer()


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "user",
        )

    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs=attrs)
        Borrowing.validate_inventory(attrs["book"], ValidationError)
        return data

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data["book"]
            if book.inventory > 0:
                book.inventory -= 1
                book.save()
            else:
                raise serializers.ValidationError("Inventory for the book is empty.")

            borrowing = Borrowing.objects.create(**validated_data)

            try:
                session_id = create_stripe_session(borrowing)
            except Exception as e:
                borrowing.delete()
                raise serializers.ValidationError(str(e))

            return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("actual_return_date",)

    def validate(self, attrs):
        data = super(BorrowingReturnSerializer, self).validate(attrs=attrs)

        if self.instance.actual_return_date:
            raise serializers.ValidationError(
                "This borrowing has already been returned."
            )

        return data

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.actual_return_date = datetime.now().date()
            instance.save()

            book = instance.book
            book.inventory += 1
            book.save()

            return instance
