from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = 'ADMIN'
    ROLE_DOCTOR = 'DOCTOR'
    ROLE_PATIENT = 'PATIENT'
    ROLE_RECEPTIONIST = 'RECEPTIONIST'
    ROLE_PHARMACIST = 'PHARMACIST'
    ROLE_LAB_TECH = 'LAB_TECH'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Hospital Administrator'),
        (ROLE_DOCTOR, 'Doctor / Specialist'),
        (ROLE_PATIENT, 'Patient'),
        (ROLE_RECEPTIONIST, 'Receptionist / Front Desk'),
        (ROLE_PHARMACIST, 'Pharmacist'),
        (ROLE_LAB_TECH, 'Laboratory Technician'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_PATIENT,
        help_text='Designates the role and permission tier of the user.'
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    @property
    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_doctor(self):
        return self.role == self.ROLE_DOCTOR

    @property
    def is_patient(self):
        return self.role == self.ROLE_PATIENT

    @property
    def is_receptionist(self):
        return self.role == self.ROLE_RECEPTIONIST

    @property
    def is_pharmacist(self):
        return self.role == self.ROLE_PHARMACIST

    @property
    def is_lab_tech(self):
        return self.role == self.ROLE_LAB_TECH

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
