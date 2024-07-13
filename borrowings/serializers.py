from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from users.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.SlugRelatedField(
        read_only=True,
        slug_field="title",
    )


class BorrowingRetrieveSerializer(BorrowingSerializer):
    book = BookSerializer()
    user = UserSerializer()


class BorrowingCreateSerializer(BorrowingSerializer):
    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs=attrs)
        Borrowing.validate_inventory(attrs["book"], ValidationError)
        return data

    def create(self, validated_data):
        with transaction.atomic():
            user = self.context["request"].user
            book = validated_data["book"]
            if book.inventory > 0:
                book.inventory -= 1
                book.save()
            else:
                raise serializers.ValidationError("Inventory for the book is empty.")
            borrowing = Borrowing.objects.create(user=user, **validated_data)
            return borrowing
