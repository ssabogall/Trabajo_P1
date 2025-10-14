from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.utils import timezone
from django.utils.timezone import now


def _money(x) -> Decimal:
    """Redondeo homogéneo a 2 decimales."""
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# =======================
# Materias primas
# =======================
class RawMaterial(models.Model):
    name = models.CharField(max_length=100)
    units = models.IntegerField(default=0)
    exp_date = models.DateField()

    def __str__(self):
        return self.name


# =======================
# Cliente
# =======================
class Customer(models.Model):
    cedula = models.CharField(max_length=30, blank=True, default="")
    nombre = models.CharField(max_length=150, blank=True, default="")
    correo = models.EmailField(blank=True, default="")

    def __str__(self):
        return self.nombre or self.cedula or "Cliente"


# =======================
# Intermedio: Producto - Materia prima (opcional)
# =======================
class ProductRawMaterial(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        unique_together = ("product", "raw_material")

    def __str__(self):
        return f"{self.product} -> {self.raw_material} ({self.quantity})"


# =======================
# Promociones
# =======================
class Promotion(models.Model):
    PERCENT = "percent"
    FIXED   = "fixed"
    DISCOUNT_TYPES = [
        (PERCENT, "Porcentaje"),
        (FIXED,   "Monto fijo"),
    ]

    name          = models.CharField(max_length=120)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default=PERCENT)
    value         = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Si es porcentaje, 10 = 10%; si es monto fijo, 10.00"
    )
    is_active     = models.BooleanField(default=True)
    starts_at     = models.DateTimeField(null=True, blank=True)
    ends_at       = models.DateTimeField(null=True, blank=True)

    # Alcance
    applies_to_all = models.BooleanField(default=False)
    products       = models.ManyToManyField("products.Product",  blank=True, related_name="promotions")
    categories     = models.ManyToManyField("products.Category", blank=True, related_name="promotions")

    # Texto amigable para admin
    def scope(self):
        if self.applies_to_all:
            return "Todos los productos"
        has_p = self.products.exists()
        has_c = self.categories.exists()
        if has_p and has_c:
            return "Productos y categorías"
        if has_p:
            return "Productos"
        if has_c:
            return "Categorías"
        return "—"
    scope.short_description = "Alcance"

    def is_currently_active(self):
        if not self.is_active:
            return False
        now_ = timezone.now()
        if self.starts_at and self.starts_at > now_:
            return False
        if self.ends_at and self.ends_at < now_:
            return False
        return True

    def __str__(self):
        return self.name


# =======================
# Orden y líneas (totales persistidos)
# =======================
class Order(models.Model):
    customer      = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    date          = models.DateTimeField(default=now)
    paymentMethod = models.CharField(max_length=100, default="Cash")

    subtotal       = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total          = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"Orden #{self.pk} - {self.date.strftime('%Y-%m-%d %H:%M')}"

    def recalc_totals(self):
        """
        Utilidad opcional para recalcular totales a partir de las líneas,
        por si no los seteaste en la vista.
        """
        sub = Decimal("0.00")
        disc = Decimal("0.00")
        tot = Decimal("0.00")
        for it in self.orderitem_set.all():
            sub += it.line_subtotal
            disc += it.line_discount
            tot += it.line_total
        self.subtotal = _money(sub)
        self.discount_total = _money(disc)
        self.total = _money(tot)
        self.save(update_fields=["subtotal", "discount_total", "total"])


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE)
    product  = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    # Totales de línea: guardamos el precio EFECTIVO aplicado
    unit_price    = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    line_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    line_discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    line_total    = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def save(self, *args, **kwargs):
        """
        Fallbacks por si la vista no envía los totales pre-calculados:
        - unit_price: si viene 0, usar el precio del producto.
        - line_subtotal = price_base * qty
        - line_total    = unit_price * qty
        - line_discount = line_subtotal - line_total
        """
        # Asegurar unit_price
        if not self.unit_price or self.unit_price == Decimal("0.00"):
            self.unit_price = _money(self.product.price)

        # Calcular totales si no vinieron
        qty = self.quantity or 0
        base_sub = _money(Decimal(self.product.price) * Decimal(qty))
        eff_total = _money(Decimal(self.unit_price) * Decimal(qty))

        if not self.line_subtotal or self.line_subtotal == Decimal("0.00"):
            self.line_subtotal = base_sub
        if not self.line_total or self.line_total == Decimal("0.00"):
            self.line_total = eff_total
        if not self.line_discount or self.line_discount == Decimal("0.00"):
            self.line_discount = _money(self.line_subtotal - self.line_total)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x{self.quantity} ({self.order.date.strftime('%Y-%m-%d %H:%M')})"
