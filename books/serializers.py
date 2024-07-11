from rest_framework import serializers

from books.models import Book


class BookSerializer(serializers.Serializer):
    class Meta:
        model = Book
        fields = ("title", "author", "cover", "inventory", "daily_fee")
