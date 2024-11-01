

# Library Management System

Library management system written in Django and Django REST Framework.

## Installation

### Clone the Repository

```bash
git clone git@github.com:saywin/library-management-api.git
cd library_management_api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Setup Database

```
export DB_HOST=<your_db_hostname>
export DB_NAME=<your_db_name>
export DB_USER=<your_db_username>
export DB_PASSWORD=<your_db_password>
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
python manage.py createsuperuser
```

# Setup Celery and Celery Beat
```
export CELERY_BROKER_URL=<your_celery_brocker_url>
export CELERY_RESULT_BACKEND=<your_result_url>
celery -A library_manage worker -l INFO --pool=solo
celery -A library_manage beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

# Getting access

To access the API endpoints, follow these steps:

1. Go to one of the following URLs:
   - [Register user](http://127.0.0.1:8000/api/user/register/)
   - [Obtain Bearer token](http://127.0.0.1:8000/api/user/token/)

2. Type in your Email & Password. For example:
   - Email address: admin@example.com
   - Password: 1qazcde3

3. After submitting your credentials, you will receive a token. This token grants access to the API endpoints.

# Available Endpoints For Users App

You can use the following endpoints:

- [Refresh Token](http://127.0.0.1:8000/api/users/token/refresh/) - This URL will refresh your token when it expires.
- [Verify Token](http://127.0.0.1:8000/api/users/token/verify/) - This URL will verify if your token is valid and has not expired.
- [User Details](http://127.0.0.1:8000/api/users/me/) - This URL will display information about yourself using the token assigned to your user.

Please note that accessing certain endpoints may require the ModHeader extension, which is available for installation in Chrome.

That's it for user endpoints. You can now proceed to the next step.

# Getting Started With DRF Library Management API

- Go to the URL provided: [API Books Endpoint](http://127.0.0.1:8000/api/books/). This URL provides authors & books creation.
- Go to the next URL provided: [API Borrowings Endpoint](http://127.0.0.1:8000/api/borrowings/create/). This URL borrowings creation.
- Go to the next URL provided: [API Borrowings Endpoint](http://127.0.0.1:8000/api/borrowings/). This URL borrowings list.
- Go to the next URL provided: [API Borrowings Endpoint](http://127.0.0.1:8000/api/borrowings/{id}/return/). This URL provides borrowings return.

Now you are ready to use the API to manage your library. Have fun!

# Features

- [x] JWT authenticated
- [x] Admin panel available at `/admin/`
- [x] Documentation located at `/api/doc/swagger/`
- [x] Manage books with authors
- [x] Create borrowings & return them
- [x] Implemented telegram bot with borrowing notifications
- [x] Implemented Celery task to check borrowings overdue
