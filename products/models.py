from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    class ProductType(models.TextChoices):
        SANDUCHE = "sanduche", "Sanduche"
        PAN_TAJADA = "pan_tajada", "Pan tajada"
        PAN = "pan", "Pan"
        OTRO = "otro", "Otro"

    name = models.CharField(max_length=120)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # ← si no lo tienes
    available = models.BooleanField(default=True)                              # ← si no lo tienes
    promotion = models.BooleanField(default=False)                             # ← si no lo tienes
    product_type = models.CharField(                                           # ← si no lo tienes
        max_length=20, choices=ProductType.choices, default=ProductType.OTRO
    )

    def __str__(self):
        return self.name
# Create your models here.
