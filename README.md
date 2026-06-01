# Luxemart

Luxemart is a Django-based e-commerce management system with customer shopping flows, administrative controls, payment review, and real-time update hooks.

## What is scaffolded

- Django project configuration with PostgreSQL support
- App structure for accounts, catalog, cart, orders, payments, dashboard, and notifications
- Shared models for timestamps, categories, products, orders, payments, delivery, and notifications
- Base templates and static assets for a bootstrap-driven UI
- Channels-ready ASGI setup for future WebSocket support
- File-based upload fields for avatars, product media, and payment proofs

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and update the values.
4. Run database migrations and start the development server.

The project now uses PostgreSQL by default. Make sure `DATABASE_URL` in `.env` points to your local `luxemart` database before running migrations.

## Useful commands

- `python manage.py check`
- `python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py runserver`
