# Luxemart

Luxemart is a Django-based e-commerce platform with a customer storefront, a management dashboard, admin-reviewed payments, order tracking, notifications, and a contact-us workflow for support and feedback.

## Overview

The project is organized as a modular Django app stack:

- `accounts` handles custom authentication, profiles, and role-based user data.
- `catalog` powers categories, products, product galleries, and the public storefront.
- `cart` manages the shopping cart and cart item totals.
- `orders` stores order history, checkout data, and delivery information.
- `payments` stores payment records, methods, approval state, and proof uploads.
- `dashboard` provides the staff management portal for products, categories, orders, users, and reports.
- `notifications` stores user notifications and contact-us submissions for admin review.
- `common` contains shared base models such as timestamps.

The project uses PostgreSQL by default, Bootstrap for the UI, Django Channels for WebSocket-ready plumbing, and local filesystem storage for media uploads.

## Main Features

- Public product listing and product detail pages
- Search, category filtering, price filtering, availability filtering, and sorting
- User registration, login, logout, and profile pages
- Shopping cart and checkout flow
- Order history and order success pages
- Payment listing and payment proof support
- Staff dashboard for catalog, order, payment, delivery, user, and report management
- Django admin support for all key data models
- Contact-us form that stores submissions in the database and shows them in admin

## Project Structure

- `manage.py` - Django command-line entry point
- `luxemart/settings.py` - project settings and environment configuration
- `luxemart/urls.py` - root URL routing
- `luxemart/asgi.py` - ASGI application with Channels support
- `apps/` - feature apps
- `templates/` - shared and app-specific templates
- `static/` - CSS, JavaScript, and images

## Environment Setup

The project expects Python 3.13 and a PostgreSQL database.

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env`.
4. Set the following environment values:
	- `SECRET_KEY`
	- `DEBUG`
	- `ALLOWED_HOSTS`
	- `DATABASE_URL`
	- `CSRF_TRUSTED_ORIGINS` if needed
5. Run migrations.
6. Start the development server.

Example commands:

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

If your PostgreSQL instance is not already created, make sure the database name in `DATABASE_URL` exists before running migrations.

## Useful Commands

- `python manage.py check`
- `python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py createsuperuser`
- `python manage.py runserver`

## Public Routes

- `/` - home page
- `/shop/` - product list
- `/shop/product/<slug>/` - product detail
- `/help/` - help center and contact form
- `/privacy/` - privacy policy
- `/terms/` - terms of service
- `/accounts/register/` - registration
- `/accounts/login/` - login
- `/accounts/logout/` - logout
- `/accounts/profile/` - user profile
- `/cart/` - cart detail
- `/cart/add/<product_id>/` - add item to cart
- `/cart/remove/<item_id>/` - remove item from cart
- `/orders/` - order history
- `/orders/checkout/` - checkout
- `/orders/success/<order_id>/` - order success page
- `/payments/` - payment list
- `/notifications/` - notification list
- `/management/` - staff dashboard home
- `/management/products/` - product management
- `/management/categories/` - category management
- `/management/orders/` - order management
- `/management/payments/` - payment management
- `/management/deliveries/` - delivery management
- `/management/users/` - user and role management
- `/management/reports/` - reports dashboard
- `/admin/` - Django admin

## Data Model Summary

### Accounts

- `Role` - named role with description and active flag
- `User` - custom user model with email, role, phone, address, city, state, zip code, avatar, and customer status

### Catalog

- `Category` - product grouping with slug, description, and active flag
- `Product` - product record with category, slug, price, stock, SKU, active/featured flags, and creator
- `ProductImage` - image gallery entries for products

### Cart

- `Cart` - one cart per user
- `CartItem` - quantity-based cart line item

### Orders

- `Order` - order header with status and total amount
- `OrderItem` - order line item with unit price and quantity
- `DeliveryInformation` - tracking and delivery status data

### Payments

- `Payment` - order payment record with method, amount, transaction ID, and approval state
- `PaymentProof` - uploaded proof files for a payment

### Notifications

- `Notification` - user notification messages
- `ContactSubmission` - contact-us form submissions with name, email, message, and reviewed flag

## Contact Us Flow

The contact-us feature lives on the help page at `/help/`.

- Users can submit their name, email, and message.
- Messages can contain issues, suggestions, feedback, or order questions.
- Submissions are saved in the `notifications_contactsubmission` table.
- Staff can review them in Django admin under the `Contact Submissions` section.

## Staff Dashboard

The staff dashboard under `/management/` is separate from Django admin and is intended for day-to-day store operations.

It provides:

- product and category CRUD
- order status management
- payment approval/rejection workflow
- delivery tracking updates
- user and role management
- revenue and sales reporting

## Django Admin

The admin site includes the main data models used by the platform, including products, orders, payments, notifications, and contact submissions.

Use `python manage.py createsuperuser` to create an admin account if one is not already present in your database.

## Media And Static Files

- Static files live in `static/`
- Templates live in `templates/`
- Uploaded media is stored under `media/`
- Collected static files are written to `staticfiles/`

## Notes

- The project is Channels-ready, but the current in-memory channel layer is suitable for development only.
- PostgreSQL is the default database backend.
- The custom user model is configured as `accounts.User`, so it should be set before the first migration in new deployments.