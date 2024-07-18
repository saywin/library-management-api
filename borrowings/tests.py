from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status, serializers
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingRetrieveSerializer,
    BorrowingReturnSerializer,
)


class BaseBorrowingAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=3,
            daily_fee=5,
        )
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="password123",
        )
        self.admin = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="password123",
        )
        self.borrowing_data = {
            "expected_return_date": (datetime.now() + timedelta(days=7)).date(),
            "book": self.book,
            "user": self.user,
        }
        self.borrowing_data_2 = {
            "expected_return_date": (datetime.now() + timedelta(days=7)).date(),
            "book": self.book.id,
            "user": self.user.id,
        }
        self.borrowing_1 = Borrowing.objects.create(**self.borrowing_data)
        self.borrowing_2 = Borrowing.objects.create(
            expected_return_date=(datetime.now() + timedelta(days=7)).date(),
            book=self.book,
            user=self.user,
        )
        self.borrowing_list_url = reverse("borrowings:borrowing-list")
        self.borrowing_detail_url = reverse(
            "borrowings:borrowing-detail", args=[self.borrowing_1.id]
        )
        self.borrowing_return_url = reverse(
            "borrowings:borrowing-return", args=[self.borrowing_1.id]
        )


class UnAuthenticatedBorrowingAPITest(BaseBorrowingAPITest):
    def test_get_borrowing_list_unauthorized(self):
        response = self.client.get(self.borrowing_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_borrowing_unauthorized(self):
        response = self.client.post(self.borrowing_list_url, self.borrowing_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingAPITest(BaseBorrowingAPITest):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_get_borrowing_list(self):
        response = self.client.get(self.borrowing_list_url)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_get_borrowing_detail(self):
        response = self.client.get(self.borrowing_detail_url)
        serializer = BorrowingRetrieveSerializer(self.borrowing_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_borrowing(self):
        create_url = reverse("borrowings:borrowing-create")
        response = self.client.post(create_url, self.borrowing_data_2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_borrowing_return(self):
        data = {"actual_return_date": datetime.now().date()}
        serializer = BorrowingReturnSerializer(instance=self.borrowing_1, data=data)
        serializer.is_valid()
        updated_instance = serializer.update(
            self.borrowing_1, serializer.validated_data
        )
        self.book.refresh_from_db()

        self.assertIsNotNone(updated_instance.actual_return_date)
        self.assertEqual(self.book.inventory, 4)


class IsAdminBorrowingApiTest(BaseBorrowingAPITest):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.admin)

    def test_list_all_existing_borrowings(self):
        Borrowing.objects.create(**self.borrowing_data)
        Borrowing.objects.create(**self.borrowing_data)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)
        response = self.client.get(self.borrowing_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_filter_borrowings_by_user_id(self):
        user_2 = get_user_model().objects.create_user(
            email="user@user.com",
            password="password123",
        )
        borrowing_3 = Borrowing.objects.create(
            expected_return_date=(datetime.now() + timedelta(days=7)).date(),
            book=self.book,
            user=user_2,
        )

        response = self.client.get(self.borrowing_list_url, {"user_id": self.user.id})

        expected_borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingListSerializer(expected_borrowings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)
        self.assertNotIn(BorrowingListSerializer(borrowing_3).data, response.data)

    def test_filter_borrowings_by_is_active(self):
        self.borrowing_2.actual_return_date = (
            (datetime.now() + timedelta(days=1)).date(),
        )

        response_active = self.client.get(
            self.borrowing_list_url, {"is_active": "true"}
        )
        response_inactive = self.client.get(
            self.borrowing_list_url, {"is_active": "false"}
        )

        active_borrowings = Borrowing.objects.filter(actual_return_date__isnull=True)
        inactive_borrowings = Borrowing.objects.filter(actual_return_date__isnull=False)

        serializer_active = BorrowingListSerializer(active_borrowings, many=True)
        serializer_inactive = BorrowingListSerializer(inactive_borrowings, many=True)

        self.assertEqual(response_active.status_code, status.HTTP_200_OK)
        self.assertEqual(response_active.data, serializer_active.data)

        self.assertEqual(response_inactive.status_code, status.HTTP_200_OK)
        self.assertEqual(response_inactive.data, serializer_inactive.data)
