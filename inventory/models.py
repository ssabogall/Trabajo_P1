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
    picture = models.ImageField( upload_to='')
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
        return self.product.name+" "+self.material.name


    class Meta:
        unique_together = ('product', 'material')

class Customer(models.Model):
    cedula = models.CharField(max_length=100)
    nombre = models.TextField(blank=True,null=True)
    correo = models.EmailField(max_length = 254,blank=True,null=True)     
        
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,null = True,blank=True)
    date = models.DateTimeField(default=now)
    paymentMethod = models.CharField(max_length=100,default="Cash")
    # amount = models.IntegerField(default=0)
    def __str__(self):
        return self.date.strftime("%Y-%m-%d %H:%M:%S")
    
    def total_amount(self):
        return sum(
            item.product.price * item.quantity for item in self.orderitem_set.all()
        )
    def products(self):
        return "\n".join(
        f"{item.product.name} ({item.quantity})" for item in self.orderitem_set.all()
    )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    def __str__(self):
        return f"{self.product.name} {self.quantity} {self.order.date.strftime("%Y-%m-%d %H:%M:%S")}"



