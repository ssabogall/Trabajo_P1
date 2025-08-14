# inventory/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderItem, ProductRawMaterial

@receiver(post_save, sender=OrderItem)
def deduct_raw_material_inventory(sender, instance, created, **kwargs):
    if created:  # Only run when new OrderItem is created
        product = instance.product
        quantity_ordered = instance.quantity

        # Get all raw materials for this product
        product_materials = ProductRawMaterial.objects.filter(product=product)

        for pm in product_materials:
            required_amount = pm.material_quantity * quantity_ordered
            raw_material = pm.material

            print(f"Deducting {required_amount} {raw_material.units} of {raw_material.name}")

            raw_material.units -= required_amount
            raw_material.save()
