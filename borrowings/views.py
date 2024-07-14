from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from borrowings.helpers import send_telegram_message
from borrowings.models import Borrowing
from borrowings.permissions import IsAdminOrOwnerUser
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingRetrieveSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)


class BorrowingCreateView(generics.CreateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)

        message = (
            f"New borrowing created for book '{borrowing.book.title}'. "
            f"Must Return: {borrowing.expected_return_date}"
        )
        send_telegram_message(message)


class BorrowingListView(generics.ListAPIView):
    serializer_class = BorrowingListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Borrowing.objects.all()

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        is_active = self.request.query_params.get("is_active", None)

        if is_active:
            queryset = queryset.filter(actual_return_date__isnull=True)

        user_id = self.request.query_params.get("user_id", None)

        if user_id and self.request.user.is_staff:
            queryset = queryset.filter(user_id=user_id)

        return queryset


class BorrowingRetrieveView(generics.RetrieveAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingRetrieveSerializer
    permission_classes = (IsAdminOrOwnerUser,)


class BorrowingReturnView(generics.UpdateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReturnSerializer
    permission_classes = (IsAdminUser,)
