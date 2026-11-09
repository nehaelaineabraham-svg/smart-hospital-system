import datetime
from django.db import models
from opd.models import Patient, Appointment


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Fully Paid'),
        ('PARTIAL', 'Partially Paid'),
    ]

    MODE_CHOICES = [
        ('CASH', 'Cash Counter'),
        ('UPI', 'UPI / QR Code'),
        ('CARD', 'Credit / Debit Card'),
        ('INSURANCE', 'Health Insurance / TPA'),
    ]

    invoice_number = models.CharField(max_length=30, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pharmacy_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    lab_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_payable = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='CASH')
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            year = datetime.date.today().year
            count = Invoice.objects.filter(created_at__year=year).count() + 1
            self.invoice_number = f"INV-{year}-{count:04d}"
        
        # Calculate totals
        self.total_amount = self.consultation_fee + self.pharmacy_fee + self.lab_fee + self.other_charges
        self.net_payable = max(0, self.total_amount - self.discount)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.patient.full_name} (₹{self.net_payable} [{self.payment_status}])"
