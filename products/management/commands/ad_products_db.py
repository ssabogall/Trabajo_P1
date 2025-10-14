# products/management/commands/ad_products_db.py
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from decimal import Decimal, InvalidOperation
import csv

from products.models import Product
try:
    from products.models import Category
except Exception:
    Category = None  # por si tu app no tiene categorías


def _to_decimal(val, default="0"):
    try:
        s = (str(val) if val is not None else "").strip()
        return Decimal(s or default)
    except (InvalidOperation, ValueError):
        return Decimal(default)


def _to_int(val, default=0):
    try:
        s = (str(val) if val is not None else "").strip()
        return int(s or default)
    except ValueError:
        return default


class Command(BaseCommand):
    help = "Carga/actualiza productos desde products.csv (ubicado en BASE_DIR)."

    def handle(self, *args, **options):
        csv_path = Path(settings.BASE_DIR) / "products.csv"
        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"No existe {csv_path}"))
            return

        product_fields = {f.name for f in Product._meta.get_fields()}
        require_category = ("category" in product_fields)  # el modelo la tiene

        created, updated, skipped = 0, 0, 0

        with csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("name") or row.get("nombre") or "").strip()
                if not name:
                    skipped += 1
                    continue

                price = _to_decimal(row.get("price") or row.get("precio") or "0")
                description_csv = (row.get("description") or row.get("descripcion") or "").strip()
                picture_csv     = (row.get("picture") or row.get("imagen") or "").strip()
                quantity_csv    = (row.get("quantity") or row.get("cantidad") or "").strip()
                quantity_val    = _to_int(quantity_csv) if quantity_csv != "" else None

                # ------ Categoría obligatoria (fallback "General") ------
                category_obj = None
                if require_category and Category is not None:
                    category_name = (row.get("category") or row.get("categoria") or "").strip()
                    if not category_name:
                        # Fallback obligatorio para cumplir NOT NULL
                        category_name = "General"
                    category_obj, _ = Category.objects.get_or_create(name=category_name)

                # ------ Construir defaults SOLO con campos existentes ------
                defaults = {"price": price}

                if "description" in product_fields and description_csv:
                    defaults["description"] = description_csv

                if "picture" in product_fields and picture_csv:
                    defaults["picture"] = picture_csv
                elif "image" in product_fields and picture_csv:
                    defaults["image"] = picture_csv
                elif "photo" in product_fields and picture_csv:
                    defaults["photo"] = picture_csv

                if "quantity" in product_fields and quantity_val is not None:
                    defaults["quantity"] = quantity_val

                if require_category and category_obj is not None:
                    defaults["category"] = category_obj

                obj, was_created = Product.objects.update_or_create(
                    name=name,
                    defaults=defaults,
                )
                created += 1 if was_created else 0
                updated += 0 if was_created else 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Productos: creados {created}, actualizados {updated}, omitidos {skipped}"
            )
        )
