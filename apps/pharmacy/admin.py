from django.contrib import admin
from .models import Medicine


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'generic_name', 'category', 'unit_price', 'stock_quantity', 'reorder_level', 'expiry_date', 'is_low_stock')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'generic_name', 'batch_number')
