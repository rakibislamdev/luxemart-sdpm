import os
import tempfile
import urllib.request
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.catalog.models import Category, Product, ProductImage
from django.conf import settings

SAMPLE_IMAGES = [
    "https://picsum.photos/seed/pic1/1200/1200",
    "https://picsum.photos/seed/pic2/1200/1200",
    "https://picsum.photos/seed/pic3/1200/1200",
    "https://picsum.photos/seed/pic4/1200/1200",
    "https://picsum.photos/seed/pic5/1200/1200",
    "https://picsum.photos/seed/pic6/1200/1200",
]

SAMPLE_PRODUCTS = [
    ("Aurora Headphones", "High-fidelity wireless headphones with active noise cancellation."),
    ("Vesper Smartwatch", "Sleek smartwatch with health tracking and AMOLED display."),
    ("Luma Lamp", "Adjustable ambient lamp with warm/cool modes."),
    ("Atlas Backpack", "Durable travel backpack with laptop compartment."),
    ("Zephyr Running Shoes", "Lightweight shoes for daily running."),
    ("Cielo Blender", "High-speed blender for smoothies and soups."),
]

CATEGORIES = [
    ("Electronics", "electronics"),
    ("Fashion", "fashion"),
    ("Home & Living", "home-living"),
    ("Sports & Fitness", "sports"),
]


class Command(BaseCommand):
    help = "Seed sample categories, products, and images for development."

    def handle(self, *args, **options):
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if not media_root:
            self.stdout.write(self.style.ERROR("MEDIA_ROOT is not configured in settings."))
            return

        with transaction.atomic():
            categories = []
            for name, slug in CATEGORIES:
                cat, created = Category.objects.get_or_create(slug=slug, defaults={"name": name})
                categories.append(cat)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created category: {name}"))

            # create products
            for idx, (title, desc) in enumerate(SAMPLE_PRODUCTS):
                cat = categories[idx % len(categories)]
                slug = slugify(title)
                product, created = Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "category": cat,
                        "name": title,
                        "description": desc,
                        "price": 49.99 + idx * 25,
                        "stock_quantity": 10 + idx * 5,
                        "sku": f"SKU-{1000+idx}",
                        "is_active": True,
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created product: {title}"))

                # attach 2 images per product; save files directly into MEDIA_ROOT/products
                for img_i in range(2):
                    url = SAMPLE_IMAGES[(idx * 2 + img_i) % len(SAMPLE_IMAGES)]
                    try:
                        tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                        urllib.request.urlretrieve(url, tmp_path)
                        media_dir = os.path.join(settings.MEDIA_ROOT, "products")
                        os.makedirs(media_dir, exist_ok=True)
                        dest_name = f"{product.slug}-{img_i}.jpg"
                        dest_path = os.path.join(media_dir, dest_name)
                        os.replace(tmp_path, dest_path)
                        img = ProductImage(product=product, is_primary=(img_i == 0))
                        img.image.name = os.path.join("products", dest_name)
                        img.save()
                        self.stdout.write(self.style.SUCCESS(f"Added image for {product.name}: {dest_name}"))
                    except Exception as e:
                        # fallback to bundled placeholder copied into media
                        try:
                            placeholder_path = os.path.join(settings.BASE_DIR, "static", "images", "placeholder.svg")
                            media_dir = os.path.join(settings.MEDIA_ROOT, "products")
                            os.makedirs(media_dir, exist_ok=True)
                            dest_name = f"{product.slug}-placeholder-{img_i}.svg"
                            dest_path = os.path.join(media_dir, dest_name)
                            with open(placeholder_path, "rb") as src, open(dest_path, "wb") as dst:
                                dst.write(src.read())
                            img = ProductImage(product=product, is_primary=(img_i == 0))
                            img.image.name = os.path.join("products", dest_name)
                            img.save()
                            self.stdout.write(self.style.WARNING(f"Used placeholder for {product.name}: {dest_name}"))
                        except Exception as e2:
                            self.stdout.write(self.style.ERROR(f"Failed to attach placeholder for {product.name}: {e2}"))

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
