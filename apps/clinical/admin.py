from django.contrib import admin
from .models import Consultation, Prescription, PrescriptionItem, LabTestOrder


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'diagnosis', 'blood_pressure', 'created_at')
    search_fields = ('patient__full_name', 'patient__uhid', 'diagnosis')
    list_filter = ('created_at',)


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'is_dispensed', 'created_at')
    inlines = [PrescriptionItemInline]
    list_filter = ('is_dispensed', 'created_at')


@admin.register(LabTestOrder)
class LabTestOrderAdmin(admin.ModelAdmin):
    list_display = ('test_name', 'patient', 'price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('test_name', 'patient__full_name', 'patient__uhid')
