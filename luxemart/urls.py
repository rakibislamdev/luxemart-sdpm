from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from apps.catalog import views as catalog_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", catalog_views.home, name="home"),
    path("privacy/", catalog_views.privacy_policy, name="privacy-policy"),
    path("terms/", catalog_views.terms_of_service, name="terms-of-service"),
    path("help/", catalog_views.help_center, name="help-center"),
    path("shop/", include("apps.catalog.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("cart/", include("apps.cart.urls")),
    path("orders/", include("apps.orders.urls")),
    path("payments/", include("apps.payments.urls")),
    path("management/", include("apps.dashboard.urls")),
    path("notifications/", include("apps.notifications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
