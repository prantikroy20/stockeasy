from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medicine_categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'suppliers'
        ordering = ['name']
    
    def __str__(self):
        return self.name
        
    @property
    def medicine_count(self):
        return self.medicines.count()

class Medicine(models.Model):
    DOSAGE_FORMS = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('cream', 'Cream'),
        ('ointment', 'Ointment'),
        ('drops', 'Drops'),
        ('inhaler', 'Inhaler'),
        ('powder', 'Powder'),
        ('other', 'Other'),
    ]
    
    PRESCRIPTION_TYPES = [
        ('prescription', 'Prescription Required'),
        ('otc', 'Over-the-Counter'),
        ('controlled', 'Controlled Substance'),
    ]
    
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    brand_name = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='medicines')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='medicines')
    
    # Medicine Details
    dosage_form = models.CharField(max_length=20, choices=DOSAGE_FORMS)
    strength = models.CharField(max_length=50, help_text='e.g., 500mg, 10ml')
    prescription_type = models.CharField(max_length=20, choices=PRESCRIPTION_TYPES, default='prescription')
    
    # Stock Information
    current_stock = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=10)
    maximum_stock = models.PositiveIntegerField(default=1000)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    # Dates
    manufacture_date = models.DateField()
    expiry_date = models.DateField()
    
    # Additional Information
    batch_number = models.CharField(max_length=50, blank=True)
    barcode = models.CharField(max_length=100, blank=True, unique=True)
    description = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    storage_instructions = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_medicines')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_medicines')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medicines'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['barcode']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['current_stock']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.strength})"
    
    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock
    
    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()
    
    @property
    def is_expiring_soon(self):
        days_until_expiry = (self.expiry_date - timezone.now().date()).days
        return 0 <= days_until_expiry <= 30
    
    @property
    def stock_status(self):
        if self.current_stock == 0:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        elif self.current_stock >= self.maximum_stock:
            return 'overstock'
        else:
            return 'normal'
    
    @property
    def profit_margin(self):
        if self.unit_price > 0:
            return ((self.selling_price - self.unit_price) / self.unit_price) * 100
        return 0
    
    def save(self, *args, **kwargs):
        # Auto-generate barcode if not provided
        if not self.barcode:
            import uuid
            self.barcode = str(uuid.uuid4())[:12].upper()
        super().save(*args, **kwargs)

class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Stock Adjustment'),
        ('expired', 'Expired Stock Removal'),
        ('damaged', 'Damaged Stock Removal'),
    ]
    
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Stock levels after transaction
    stock_before = models.PositiveIntegerField()
    stock_after = models.PositiveIntegerField()
    
    # Additional Information
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['medicine', '-created_at']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.medicine.name} - {self.get_transaction_type_display()} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        # Calculate total amount if not provided
        if self.unit_price and not self.total_amount:
            self.total_amount = self.unit_price * abs(self.quantity)
        
        # Update medicine stock
        if self.pk is None:  # New transaction
            self.stock_before = self.medicine.current_stock
            
            if self.transaction_type in ['purchase', 'return']:
                self.medicine.current_stock += abs(self.quantity)
            elif self.transaction_type in ['sale', 'expired', 'damaged']:
                self.medicine.current_stock -= abs(self.quantity)
            elif self.transaction_type == 'adjustment':
                self.medicine.current_stock = abs(self.quantity)
            
            self.stock_after = max(0, self.medicine.current_stock)
            self.medicine.current_stock = self.stock_after
            self.medicine.save()
        
        super().save(*args, **kwargs)

class Alert(models.Model):
    ALERT_TYPES = [
        ('low_stock', 'Low Stock'),
        ('expired', 'Expired Medicine'),
        ('expiring_soon', 'Expiring Soon'),
        ('out_of_stock', 'Out of Stock'),
    ]
    
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_type', 'is_resolved']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.medicine.name} - {self.get_alert_type_display()}"