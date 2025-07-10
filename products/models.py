from django.db import models
from django.core.validators import MinValueValidator
# from django.utils.translation import gettext_lazy as _
from users.models import *

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'SUPPLIER'})
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'CUSTOMER'}, related_name='orders')
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField()
    delivery_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                      limit_choices_to={'role': 'DELIVERY'})
    
    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"

class DeliveryAssignment(models.Model):
    delivery_person = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DELIVERY'})
    orders = models.ManyToManyField(Order)
    assigned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Order.STATUS_CHOICES, default='PENDING')
    def save(self, *args, **kwargs):  ##once status saved sabai tira status change hunalai 
        super().save(*args, **kwargs)
        for order in self.orders.all():
            order.status = self.status
            order.save()