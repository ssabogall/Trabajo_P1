from django.db import models
from django.utils import timezone
from django.utils.timezone import now


class RawMaterial(models.Model):
    name = models.CharField(max_length=100)
    units = models.IntegerField(default=0)
    exp_date = models.DateField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True,null=True)
    price = models.DecimalField(max_digits=7, decimal_places=0)
    quantity = models.PositiveIntegerField(default=0)
    picture = models.ImageField(upload_to='')
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

    def __str__(self):
        return self.product.name + " " + self.material.name

    class Meta:
        unique_together = ('product', 'material')


class Customer(models.Model):
    cedula = models.CharField(max_length=100)
    nombre = models.TextField(blank=True,null=True)
    correo = models.EmailField(max_length=254, blank=True, null=True)


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(default=now)
    paymentMethod = models.CharField(max_length=100, default="Cash")
    # amount = models.IntegerField(default=0)

    def __str__(self):
        return self.date.strftime("%Y-%m-%d %H:%M:%S")

    def total_amount(self):
        # [[MODIFICADO]] antes: sum(item.product.price * item.quantity ...)
        return sum(
            ((item.unit_price or item.product.price) * item.quantity) for item in self.orderitem_set.all()
        )

    def products(self):
        return "\n".join(
            f"{item.product.name} ({item.quantity})" for item in self.orderitem_set.all()
        )


class OrderItem(models.Model):
    # [[AGREGADO]] unit_price: precio unitario congelado al momento de la venta (con promo)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} {self.quantity} {self.order.date.strftime('%Y-%m-%d %H:%M:%S')}"


class Comment(models.Model):
    product = models.ForeignKey(Product, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    name = models.TextField()
    # score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


# [[AGREGADO]] Promociones
class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('fixed', 'Monto fijo'),
        ('percent', 'Porcentaje'),
    ]
    name = models.CharField(max_length=100)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='fixed')
    value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    applies_to_all = models.BooleanField(default=False)
    products = models.ManyToManyField(Product, blank=True, related_name='promotions')

    def is_current(self):
        now_ = timezone.now()
        if not self.is_active:
            return False
        if self.starts_at and now_ < self.starts_at:
            return False
        if self.ends_at and now_ > self.ends_at:
            return False
        return True

    def applies_to(self, product):
        return self.applies_to_all or self.products.filter(pk=product.pk).exists()

    def __str__(self):
        return self.name


# =========================
# [[AGREGADO PB-27]] Rating
# =========================
class Rating(models.Model):
    """
    Calificación por usuario (Customer) y producto.
    Solo se crea/actualiza si el producto pertenece a alguna orden del mismo customer.
    """
    product = models.ForeignKey(Product, related_name='ratings', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, related_name='ratings', on_delete=models.CASCADE)
    stars = models.PositiveSmallIntegerField(default=0)  # 1..5
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'customer')
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"

    def __str__(self):
        nombre = self.customer.nombre or self.customer.cedula
        return f"{nombre} → {self.product.name}: {self.stars}★"
