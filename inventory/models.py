from django.db import models

class RawMaterial(models.Model):
    name = models.CharField(max_length=100)
    units = models.CharField(max_length=50)
    exp_date = models.DateField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=0)
    quantity = models.PositiveIntegerField(default=0)
    picture = models.ImageField(blank=True, null=True, upload_to='')
    raw_materials = models.ManyToManyField(
        'RawMaterial',
        related_name='products',
        through='ProductRawMaterial'
    )

    def __str__(self):
        return self.name


class ProductRawMaterial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    material_quantity = models.FloatField()

    class Meta:
        unique_together = ('product', 'material')

    def __str__(self):
        return f"{self.material_quantity} de {self.material.name} para {self.product.name}"