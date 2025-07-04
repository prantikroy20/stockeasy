from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Category, Supplier, Medicine, StockTransaction, Alert

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'medicine_count', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def medicine_count(self, obj):
        return obj.medicines.count()
    medicine_count.short_description = 'Medicines'

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'is_active', 'medicine_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'contact_person', 'email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_person', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def medicine_count(self, obj):
        return obj.medicines.count()
    medicine_count.short_description = 'Medicines'

class StockTransactionInline(admin.TabularInline):
    model = StockTransaction
    extra = 0
    readonly_fields = ('stock_before', 'stock_after', 'total_amount', 'created_at')
    fields = ('transaction_type', 'quantity', 'unit_price', 'total_amount', 'stock_before', 'stock_after', 'created_by', 'created_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'supplier', 'dosage_form', 'strength',
        'current_stock', 'stock_status_display', 'expiry_status_display',
        'selling_price', 'is_active'
    )
    list_filter = (
        'category', 'supplier', 'dosage_form', 'prescription_type',
        'is_active', 'created_at', 'expiry_date'
    )
    search_fields = ('name', 'generic_name', 'brand_name', 'barcode')
    readonly_fields = ('created_at', 'updated_at', 'profit_margin')
    inlines = [StockTransactionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'generic_name', 'brand_name', 'category', 'supplier')
        }),
        ('Medicine Details', {
            'fields': ('dosage_form', 'strength', 'prescription_type')
        }),
        ('Stock Information', {
            'fields': ('current_stock', 'minimum_stock', 'maximum_stock')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'selling_price', 'profit_margin')
        }),
        ('Dates', {
            'fields': ('manufacture_date', 'expiry_date')
        }),
        ('Additional Information', {
            'fields': ('batch_number', 'barcode', 'description', 'side_effects', 'storage_instructions')
        }),
        ('Status & Tracking', {
            'fields': ('is_active', 'created_by', 'updated_by', 'created_at', 'updated_at')
        })
    )
    
    def stock_status_display(self, obj):
        status = obj.stock_status
        colors = {
            'out_of_stock': 'red',
            'low_stock': 'orange',
            'normal': 'green',
            'overstock': 'blue'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(status, 'black'),
            status.replace('_', ' ').title()
        )
    stock_status_display.short_description = 'Stock Status'
    
    def expiry_status_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red; font-weight: bold;">Expired</span>')
        elif obj.is_expiring_soon:
            return format_html('<span style="color: orange; font-weight: bold;">Expiring Soon</span>')
        else:
            return format_html('<span style="color: green;">Valid</span>')
    expiry_status_display.short_description = 'Expiry Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'supplier', 'created_by', 'updated_by')

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'medicine', 'transaction_type', 'quantity', 'unit_price',
        'total_amount', 'stock_before', 'stock_after', 'created_by', 'created_at'
    )
    list_filter = ('transaction_type', 'created_at', 'medicine__category')
    search_fields = ('medicine__name', 'reference_number', 'notes')
    readonly_fields = ('stock_before', 'stock_after', 'total_amount', 'created_at')
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('medicine', 'transaction_type', 'quantity', 'unit_price', 'total_amount')
        }),
        ('Stock Levels', {
            'fields': ('stock_before', 'stock_after')
        }),
        ('Additional Information', {
            'fields': ('reference_number', 'notes')
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('medicine', 'created_by')

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'alert_type', 'is_resolved', 'created_at', 'resolved_by')
    list_filter = ('alert_type', 'is_resolved', 'created_at')
    search_fields = ('medicine__name', 'message')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('medicine', 'resolved_by')

# Customize admin site
admin.site.site_header = "Medicine Stock Management Admin"
admin.site.site_title = "Medicine Stock Admin"
admin.site.index_title = "Welcome to Medicine Stock Management"