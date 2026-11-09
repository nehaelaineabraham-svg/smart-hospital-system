from django.contrib import admin
from .models import Department, Doctor, Patient, Appointment


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'floor_number', 'is_active')
    search_fields = ('name', 'code')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'specialization', 'consultation_fee', 'room_number', 'is_available')
    list_filter = ('department', 'is_available')
    search_fields = ('user__first_name', 'user__last_name', 'specialization')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('uhid', 'full_name', 'gender', 'dob', 'contact_number', 'blood_group')
    search_fields = ('uhid', 'full_name', 'contact_number')
    list_filter = ('gender', 'blood_group')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('token_number', 'patient', 'doctor', 'department', 'appointment_date', 'status')
    list_filter = ('status', 'department', 'appointment_date')
    search_fields = ('token_number', 'patient__full_name', 'patient__uhid')
