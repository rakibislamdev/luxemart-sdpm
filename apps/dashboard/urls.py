from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.products, name="products"),
    path("categories/", views.categories, name="categories"),
    path("orders/", views.orders, name="orders"),
    path("payments/", views.payments, name="payments"),
    path("deliveries/", views.deliveries, name="deliveries"),
    path("users/", views.users, name="users"),
    path("reports/", views.reports, name="reports"),
]
