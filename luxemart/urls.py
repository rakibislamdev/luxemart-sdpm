from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.catalog.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("cart/", include("apps.cart.urls")),
    path("orders/", include("apps.orders.urls")),
    path("payments/", include("apps.payments.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("notifications/", include("apps.notifications.urls")),
]
