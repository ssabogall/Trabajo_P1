from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from decimal import Decimal, InvalidOperation
import csv

from products.models import Product
from inventory.models import RawMaterial, ProductRawMaterial


def _find_product(name_or_code: str):
    """Busca producto por nombre (iexact/contains) y por prefijo de código '1234 - ...'."""
    s = (name_or_code or "").strip()
    if not s:
        return None
    # 1) nombre exacto (case-insensitive)
    prod = Product.objects.filter(name__iexact=s).first()
    if prod:
        return prod
    # 2) si viene con código al inicio '1007 - ...'
    if "-" in s:
        code = s.split("-", 1)[0].strip()
        if code:
            # empieza exactamente por '1007 -'
            prod = Product.objects.filter(name__istartswith=code + " -").first()
            if prod:
                return prod
    # 3) contains (fallback)
    return Product.objects.filter(name__icontains=s).first()


def _find_material(name: str):
    s = (name or "").strip()
    if not s:
        return None
    return (
        RawMaterial.objects.filter(name__iexact=s).first()
        or RawMaterial.objects.filter(name__icontains=s).first()
    )


class Command(BaseCommand):
    help = "Crea/actualiza la relación producto-materia desde products_material.csv"

    def handle(self, *args, **options):
        csv_path = Path(settings.BASE_DIR) / "products_material.csv"
        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"No existe {csv_path}"))
            return

        created, updated, skipped = 0, 0, 0

        with csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                prod_name = (row.get("product") or row.get("producto") or "").strip()
                mat_name = (row.get("material") or row.get("materia") or "").strip()
                qty_raw = (row.get("quantity") or row.get("cantidad") or "0").strip()
                try:
                    qty = Decimal(qty_raw)
                except (InvalidOperation, ValueError):
                    qty = Decimal("0")

                product = _find_product(prod_name)
                material = _find_material(mat_name)

                if not product:
                    self.stderr.write(self.style.WARNING(f"SKIP producto no encontrado: {prod_name!r}"))
                    skipped += 1
                    continue
                if not material:
                    self.stderr.write(self.style.WARNING(f"SKIP material no encontrado: {mat_name!r}"))
                    skipped += 1
                    continue

                # IMPORTANTE: usamos los nombres actuales del modelo:
                # product, raw_material, quantity
                obj, was_created = ProductRawMaterial.objects.update_or_create(
                    product=product,
                    raw_material=material,
                    defaults={"quantity": qty},
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"ProductRawMaterial: creados {created}, actualizados {updated}, omitidos {skipped}"
            )
        )
