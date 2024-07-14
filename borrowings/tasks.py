from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from borrowings.helpers import send_telegram_message
from borrowings.models import Borrowing


@shared_task
def check_overdue_borrowings():
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=tomorrow, actual_return_date__isnull=True
    )

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            book_title = borrowing.book.title
            user = f"{borrowing.user.first_name} {borrowing.user.last_name}"
            email = borrowing.user.email
            return_date = borrowing.expected_return_date
            message = (
                f"Overdue borrowing:\n"
                f"User: {user}\nBook: {book_title}\n"
                f"Email user: {borrowing.user.email}\n"
                f"Return date: {return_date}"
            )
            send_telegram_message(message)
    else:
        send_telegram_message("No borrowings overdue today!")
