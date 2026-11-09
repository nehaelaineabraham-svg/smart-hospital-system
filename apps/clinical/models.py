from django.db import models
from opd.models import Patient, Doctor, Appointment
from pharmacy.models import Medicine


class Consultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='consultation')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='consultations')
    
    # Clinical Vitals
    blood_pressure = models.CharField(max_length=20, blank=True, null=True, help_text="e.g. 120/80 mmHg")
    pulse_rate = models.CharField(max_length=20, blank=True, null=True, help_text="e.g. 72 bpm")
    temperature = models.CharField(max_length=20, blank=True, null=True, help_text="e.g. 98.6 F")
    spo2 = models.CharField(max_length=20, blank=True, null=True, help_text="e.g. 99%")

    chief_complaints = models.TextField()
    clinical_findings = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(help_text="Provisional or confirmed diagnosis")
    follow_up_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation for {self.patient.full_name} by {self.doctor} ({self.created_at.strftime('%d-%b-%Y')})"


class Prescription(models.Model):
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='prescription')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    general_advice = models.TextField(blank=True, null=True, help_text="Dietary advice, precautions, lifestyle changes")
    is_dispensed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription #{self.id} for {self.patient.full_name}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name='prescribed_items')
    dosage = models.CharField(max_length=50, default='1-0-1', help_text="Morning - Afternoon - Night")
    duration = models.CharField(max_length=50, default='5 days')
    quantity = models.PositiveIntegerField(default=10, help_text="Total units to dispense")
    instructions = models.CharField(max_length=150, default='After meals')

    def __str__(self):
        return f"{self.medicine.name} - {self.dosage} for {self.duration}"


class LabTestOrder(models.Model):
    STATUS_CHOICES = [
        ('ORDERED', 'Ordered by Doctor'),
        ('SAMPLE_COLLECTED', 'Sample Collected'),
        ('IN_PROCESS', 'Testing In Process'),
        ('COMPLETED', 'Report Ready'),
    ]

    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='lab_orders')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_orders')
    test_name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=300.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ORDERED')
    findings = models.TextField(blank=True, null=True)
    normal_range = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.test_name} for {self.patient.full_name} [{self.status}]"
