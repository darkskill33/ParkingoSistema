# ParkingoSistema

ParkingoSistema is a Django-based smart parking reservation system developed as a course project for Intelligent Device Programming. The application allows registered users to search available parking locations, reserve approved parking spots by date range, complete payments through Stripe, and manage reservations from a personal profile.

## Key Features

- User registration, login, and profile management using Django authentication
- Browsing and filtering parking locations with approved parking spots
- Reservation validation with conflict detection and date-range availability checks
- Stripe payment integration for checkout and reservation confirmation
- Parking location reviews and spot approval workflow
- Background reservation cleanup with Celery task scheduling
- Admin panel support for managing users, parking spots, locations, and reservations

## Technologies

- Python 3
- Django 5.1
- SQLite
- Stripe API
- Celery
- Django templates and Bootstrap-friendly UI

## Project Structure

- `parking/` — core reservation models, views, templates, and Celery task logic
- `users/` — user registration, authentication, and profile management
- `parkingosistema/` — Django project settings and URL configuration
- `db.sqlite3` — local development database

## Installation

1. Clone the repository:

```bash
git clone https://github.com/darkskill33/ParkingoSistema.git
cd ParkingoSistema
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install project dependencies:

```bash
pip install django celery stripe
```

4. Apply database migrations:

```bash
python manage.py migrate
```

5. Create a Django superuser:

```bash
python manage.py createsuperuser
```

## Running the Application

Start the Django development server:

```bash
python manage.py runserver
```

Open the application at `http://127.0.0.1:8000/` and the admin interface at `http://127.0.0.1:8000/admin/`.

## Notes

- The project uses SQLite for local development.
- Stripe test API keys are configured in `parkingosistema/settings.py` for payment flow testing.
- Celery is used for scheduled cleanup of unpaid reservations.

