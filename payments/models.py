from django.db import models
from django.urls import reverse

from borrowings.models import Borrowing


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"

    class TypeChoices(models.TextChoices):
        PAYMENT = "PAYMENT"
        FINE = "FINE"

    status = models.CharField(max_length=10, choices=StatusChoices.choices)
    type = models.CharField(max_length=10, choices=StatusChoices.choices)
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField(null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_type_display()} - {self.status}"

    def get_absolute_url(self):
        return reverse("payment-detail", args=[str(self.id)])

    @staticmethod
    def calculate_fine(borrowing):
        if borrowing.actual_return_date > borrowing.expected_return_date:
            days_of_overdue = (
                borrowing.actual_return_date - borrowing.expected_return_date
            ).days
            fine_multiplier = 1.1
            daily_fee = borrowing.book.daily_fee
            fine_amount = days_of_overdue * daily_fee * fine_multiplier
            return fine_amount
        else:
            return 0
