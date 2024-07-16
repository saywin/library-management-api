from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer


class BaseBookAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book_1 = Book.objects.create(
            title="Book Test",
            author="Author Test",
            cover="HARD",
            inventory=3,
            daily_fee=5,
        )
        self.new_book_data = {
            "title": "New Book Test",
            "author": "New Author Test",
            "cover": "HARD",
            "inventory": 7,
            "daily_fee": 10,
        }
        self.book_list_url = reverse("books:book-list")
        self.book_detail_url = reverse("books:book-detail", args=[self.book_1.id])


class UnAuthenticatedBooksApiTest(BaseBookAPITest):

    def test_get_books_list_and_serializer_unauthorized(self):
        response = self.client.get(self.book_list_url)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_get_book_detail_unauthorized(self):
        response = self.client.get(self.book_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_unauthorized(self):
        response = self.client.post(self.book_list_url, self.new_book_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBooksApiTest(BaseBookAPITest):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            email="user@user.com",
            password="1qazcde3"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_book_detail_unauthorized_forbidden(self):
        response = self.client.get(self.book_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookAPITest(BaseBookAPITest):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="1qazcde3",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_get_book_detail_admin(self):
        response = self.client.get(self.book_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book_admin(self):
        response = self.client.post(self.book_list_url, self.new_book_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_book_admin(self):
        response = self.client.delete(self.book_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
