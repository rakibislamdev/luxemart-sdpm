from django import forms
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from apps.accounts.models import Role
from apps.catalog.models import Category, Product
from apps.orders.models import DeliveryInformation, Order
from apps.payments.models import Payment


class LuxeModelForm(forms.ModelForm):
    field_class = "form-control"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", self.field_class)
            if field.required:
                widget.attrs.setdefault("data-required", "true")


def unique_slug(model, value, instance=None):
    base_slug = slugify(value)[:45] or "item"
    slug = base_slug
    index = 2
    queryset = model.objects.all()
    if instance and instance.pk:
        queryset = queryset.exclude(pk=instance.pk)
    while queryset.filter(slug=slug).exists():
        slug = f"{base_slug}-{index}"
        index += 1
    return slug


class CategoryForm(LuxeModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = Category
        fields = ("name", "slug", "description", "is_active")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        name = self.cleaned_data.get("name")
        return slug or unique_slug(Category, name, self.instance)


class ProductForm(LuxeModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = Product
        fields = (
            "category",
            "name",
            "slug",
            "sku",
            "price",
            "stock_quantity",
            "description",
            "is_active",
            "featured",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "stock_quantity": forms.NumberInput(attrs={"min": "0"}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        name = self.cleaned_data.get("name")
        return slug or unique_slug(Product, name, self.instance)


class UserManagementForm(LuxeModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "is_active",
            "is_staff",
            "is_active_customer",
        )


class RoleForm(LuxeModelForm):
    class Meta:
        model = Role
        fields = ("name", "description", "is_active")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class OrderStatusForm(LuxeModelForm):
    class Meta:
        model = Order
        fields = ("status",)


class PaymentStatusForm(LuxeModelForm):
    class Meta:
        model = Payment
        fields = ("status",)


class DeliveryInformationForm(LuxeModelForm):
    delivered_at = forms.DateTimeField(required=False, input_formats=["%Y-%m-%dT%H:%M"])

    class Meta:
        model = DeliveryInformation
        fields = ("status", "carrier", "tracking_number", "delivered_at")
        widgets = {
            "delivered_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }
