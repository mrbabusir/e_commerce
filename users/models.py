from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('SUPPLIER', 'Supplier'),
        ('CUSTOMER', 'Customer'),
        ('DELIVERY', 'Delivery Personnel'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CUSTOMER')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.username}"