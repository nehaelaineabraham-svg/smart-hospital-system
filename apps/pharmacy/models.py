import datetime
from django.db import models


class Medicine(models.Model):
    CATEGORY_CHOICES = [
        ('TABLET', 'Tablet'),
        ('CAPSULE', 'Capsule'),
        ('SYRUP', 'Syrup'),
        ('INJECTION', 'Injection'),
        ('OINTMENT', 'Ointment / Cream'),
        ('DROPS', 'Drops'),
        ('INHALER', 'Inhaler'),
    ]

    name = models.CharField(max_length=150, unique=True)
    generic_name = models.CharField(max_length=150, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='TABLET')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    stock_quantity = models.PositiveIntegerField(default=100)
    reorder_level = models.PositiveIntegerField(default=20, help_text="Alert trigger when stock falls below this amount")
    batch_number = models.CharField(max_length=50, default='BTH-001')
    expiry_date = models.DateField(default=datetime.date.today)
    is_active = models.BooleanField(default=True)

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level

    @property
    def is_expired(self):
        return self.expiry_date <= datetime.date.today()

    def __str__(self):
        return f"{self.name} (Stock: {self.stock_quantity})"
