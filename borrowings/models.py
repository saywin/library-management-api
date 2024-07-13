from django.conf import settings
from django.db import models
from django.db.models import Q, F
from rest_framework.exceptions import ValidationError

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                        Q(expected_return_date__gte=F("borrow_date"))
                        & Q(actual_return_date__gte=F("borrow_date"))
                ),
                name="return_date_gte_borrow_date", )
        ]

    @staticmethod
    def validate_inventory(book: Book, error_to_raise):
        if book.inventory <= 0:
            raise error_to_raise(
                f"All books with the title - {book.title} "
                f"are currently unavailable"
            )

    def clean(self):
        Borrowing.validate_inventory(self.book, ValidationError)
        if self.actual_return_date and self.actual_return_date < self.borrow_date:
            raise ValidationError("Actual return date cannot be earlier than borrow date.")

    def __str__(self):
        return f"{self.book.title}, {self.expected_return_date}"
