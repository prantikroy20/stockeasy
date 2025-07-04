from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Medicine, Category, Supplier, StockTransaction

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name', 'generic_name', 'brand_name', 'category', 'supplier',
            'dosage_form', 'strength', 'prescription_type',
            'current_stock', 'minimum_stock', 'maximum_stock',
            'unit_price', 'selling_price',
            'manufacture_date', 'expiry_date',
            'batch_number', 'barcode',
            'description', 'side_effects', 'storage_instructions',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Medicine Name'}),
            'generic_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Generic Name'}),
            'brand_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand Name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'dosage_form': forms.Select(attrs={'class': 'form-control'}),
            'strength': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 500mg, 10ml'}),
            'prescription_type': forms.Select(attrs={'class': 'form-control'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'maximum_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'manufacture_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Batch Number'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Barcode (optional)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'side_effects': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'storage_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        manufacture_date = cleaned_data.get('manufacture_date')
        expiry_date = cleaned_data.get('expiry_date')
        minimum_stock = cleaned_data.get('minimum_stock')
        maximum_stock = cleaned_data.get('maximum_stock')
        unit_price = cleaned_data.get('unit_price')
        selling_price = cleaned_data.get('selling_price')
        
        # Validate dates
        if manufacture_date and expiry_date:
            if manufacture_date >= expiry_date:
                raise ValidationError('Expiry date must be after manufacture date.')
            
            if expiry_date <= timezone.now().date():
                raise ValidationError('Expiry date cannot be in the past.')
        
        # Validate stock levels
        if minimum_stock and maximum_stock:
            if minimum_stock >= maximum_stock:
                raise ValidationError('Maximum stock must be greater than minimum stock.')
        
        # Validate prices
        if unit_price and selling_price:
            if selling_price < unit_price:
                raise ValidationError('Selling price should not be less than unit price.')
        
        return cleaned_data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier Name'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class StockTransactionForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ['medicine', 'transaction_type', 'quantity', 'unit_price', 'reference_number', 'notes']
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reference Number'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active medicines
        self.fields['medicine'].queryset = Medicine.objects.filter(is_active=True)
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        transaction_type = self.cleaned_data.get('transaction_type')
        medicine = self.cleaned_data.get('medicine')
        
        if quantity and transaction_type and medicine:
            if transaction_type in ['sale', 'expired', 'damaged']:
                if quantity > medicine.current_stock:
                    raise ValidationError(
                        f'Cannot {transaction_type} {quantity} units. '
                        f'Only {medicine.current_stock} units available in stock.'
                    )
        
        return quantity

class MedicineSearchForm(forms.Form):
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search medicines by name, generic name, or barcode...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.filter(is_active=True),
        required=False,
        empty_label='All Suppliers',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    dosage_form = forms.ChoiceField(
        choices=[('', 'All Forms')] + Medicine.DOSAGE_FORMS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    prescription_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Medicine.PRESCRIPTION_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    stock_status = forms.ChoiceField(
        choices=[
            ('', 'All Stock Levels'),
            ('low_stock', 'Low Stock'),
            ('out_of_stock', 'Out of Stock'),
            ('normal', 'Normal Stock'),
            ('overstock', 'Overstock'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    expiry_status = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('expired', 'Expired'),
            ('expiring_soon', 'Expiring Soon (30 days)'),
            ('valid', 'Valid'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class BulkUpdateForm(forms.Form):
    medicines = forms.ModelMultipleChoiceField(
        queryset=Medicine.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    action = forms.ChoiceField(
        choices=[
            ('activate', 'Activate'),
            ('deactivate', 'Deactivate'),
            ('update_prices', 'Update Prices'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price_increase_percentage = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )