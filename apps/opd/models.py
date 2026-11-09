import datetime
from django.db import models
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Prefix for tokens, e.g., CARD, NEUR, GEN")
    floor_number = models.PositiveSmallIntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='doctors')
    specialization = models.CharField(max_length=120)
    qualification = models.CharField(max_length=120, help_text="e.g. MBBS, MD, DM")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    room_number = models.CharField(max_length=20, default='OPD-101')
    available_days = models.CharField(max_length=100, default='Mon - Sat')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.department.name}"


class Patient(models.Model):
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='patient_profile')
    uhid = models.CharField(max_length=30, unique=True, editable=False, help_text="Universal Health Identification Number")
    full_name = models.CharField(max_length=150)
    dob = models.DateField(verbose_name="Date of Birth")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    contact_number = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    medical_allergies = models.TextField(blank=True, null=True, help_text="Known drug or food allergies")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.uhid:
            # Generate UHID: MF-YYYY-XXXX
            year = datetime.date.today().year
            count = Patient.objects.filter(created_at__year=year).count() + 1
            self.uhid = f"MF-{year}-{count:04d}"
        super().save(*args, **kwargs)

    @property
    def age(self):
        today = datetime.date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    def __str__(self):
        return f"{self.full_name} [{self.uhid}]"


class Appointment(models.Model):
    STATUS_SCHEDULED = 'SCHEDULED'
    STATUS_CHECKED_IN = 'CHECKED_IN'
    STATUS_IN_WAITING = 'IN_WAITING'
    STATUS_ENGAGED = 'ENGAGED'
    STATUS_CONSULTED = 'CONSULTED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_CHECKED_IN, 'Checked In at Reception'),
        (STATUS_IN_WAITING, 'Waiting for Doctor'),
        (STATUS_ENGAGED, 'In Consultation Cabin'),
        (STATUS_CONSULTED, 'Consultation Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField(default=datetime.date.today)
    token_number = models.CharField(max_length=20, editable=False)
    token_sequence = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    symptoms = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['appointment_date', 'token_sequence']

    def save(self, *args, **kwargs):
        if not self.token_number:
            # Auto-assign next token sequence for this doctor & department on this date
            dept_code = self.department.code if self.department else 'GEN'
            existing_count = Appointment.objects.filter(
                department=self.department,
                appointment_date=self.appointment_date
            ).count()
            self.token_sequence = existing_count + 1
            self.token_number = f"{dept_code}-{self.token_sequence:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Token #{self.token_number} - {self.patient.full_name} with {self.doctor} ({self.status})"
