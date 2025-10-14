from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from datetime import datetime
import csv

from inventory.models import RawMaterial


class Command(BaseCommand):
    help = "Carga/actualiza materias primas desde materials.csv"

    def handle(self, *args, **options):
        csv_path = Path(settings.BASE_DIR) / "materials.csv"
        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"No existe {csv_path}"))
            return

        created, updated, skipped = 0, 0, 0

        with csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("name") or row.get("nombre") or "").strip()
                if not name:
                    skipped += 1
                    continue

                # units (entero, tolerante)
                units_raw = (row.get("units") or row.get("unidades") or "0").strip()
                try:
                    units = int(units_raw)
                except ValueError:
                    units = 0

                # exp_date (opcional; varios formatos)
                exp_str = (row.get("exp_date") or row.get("fecha_exp") or "").strip()
                exp_date = None
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
                    if not exp_str:
                        break
                    try:
                        exp_date = datetime.strptime(exp_str, fmt).date()
                        break
                    except ValueError:
                        continue

                defaults = {"units": units}
                if hasattr(RawMaterial, "exp_date") and exp_date is not None:
                    defaults["exp_date"] = exp_date

                obj, was_created = RawMaterial.objects.update_or_create(
                    name=name,
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"RawMaterial: creados {created}, actualizados {updated}, omitidos {skipped}"
            )
        )
