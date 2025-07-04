from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from accounts.decorators import staff_or_above_required, pharmacist_or_admin_required, admin_required
from .models import Medicine, Category, Supplier, StockTransaction, Alert
from .forms import (
    MedicineForm, CategoryForm, SupplierForm, 
    StockTransactionForm, MedicineSearchForm, BulkUpdateForm
)
import json
from datetime import datetime, timedelta

@login_required
def medicine_list(request):
    form = MedicineSearchForm(request.GET)
    medicines = Medicine.objects.select_related('category', 'supplier').all()
    
    # Apply filters
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        supplier = form.cleaned_data.get('supplier')
        dosage_form = form.cleaned_data.get('dosage_form')
        prescription_type = form.cleaned_data.get('prescription_type')
        stock_status = form.cleaned_data.get('stock_status')
        expiry_status = form.cleaned_data.get('expiry_status')
        
        if search:
            medicines = medicines.filter(
                Q(name__icontains=search) |
                Q(generic_name__icontains=search) |
                Q(brand_name__icontains=search) |
                Q(barcode__icontains=search)
            )
        
        if category:
            medicines = medicines.filter(category=category)
        
        if supplier:
            medicines = medicines.filter(supplier=supplier)
        
        if dosage_form:
            medicines = medicines.filter(dosage_form=dosage_form)
        
        if prescription_type:
            medicines = medicines.filter(prescription_type=prescription_type)
        
        if stock_status:
            if stock_status == 'low_stock':
                medicines = medicines.filter(current_stock__lte=F('minimum_stock'))
            elif stock_status == 'out_of_stock':
                medicines = medicines.filter(current_stock=0)
            elif stock_status == 'overstock':
                medicines = medicines.filter(current_stock__gte=F('maximum_stock'))
            elif stock_status == 'normal':
                medicines = medicines.filter(
                    current_stock__gt=F('minimum_stock'),
                    current_stock__lt=F('maximum_stock')
                )
        
        if expiry_status:
            today = timezone.now().date()
            if expiry_status == 'expired':
                medicines = medicines.filter(expiry_date__lt=today)
            elif expiry_status == 'expiring_soon':
                thirty_days_later = today + timedelta(days=30)
                medicines = medicines.filter(
                    expiry_date__gte=today,
                    expiry_date__lte=thirty_days_later
                )
            elif expiry_status == 'valid':
                thirty_days_later = today + timedelta(days=30)
                medicines = medicines.filter(expiry_date__gt=thirty_days_later)
    
    # Pagination
    paginator = Paginator(medicines, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_medicines': medicines.count(),
    }
    return render(request, 'medicines/medicine_list.html', context)

@login_required
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    recent_transactions = medicine.transactions.all()[:10]
    
    context = {
        'medicine': medicine,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'medicines/medicine_detail.html', context)

@login_required
@staff_or_above_required
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.created_by = request.user
            medicine.updated_by = request.user
            medicine.save()
            
            # Create initial stock transaction
            if medicine.current_stock > 0:
                StockTransaction.objects.create(
                    medicine=medicine,
                    transaction_type='purchase',
                    quantity=medicine.current_stock,
                    unit_price=medicine.unit_price,
                    stock_before=0,
                    stock_after=medicine.current_stock,
                    created_by=request.user,
                    notes='Initial stock entry'
                )
            
            messages.success(request, f'Medicine "{medicine.name}" created successfully!')
            return redirect('medicines:detail', pk=medicine.pk)
    else:
        form = MedicineForm()
    
    return render(request, 'medicines/medicine_form.html', {
        'form': form,
        'title': 'Add New Medicine'
    })

@login_required
@staff_or_above_required
def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.updated_by = request.user
            medicine.save()
            messages.success(request, f'Medicine "{medicine.name}" updated successfully!')
            return redirect('medicines:detail', pk=medicine.pk)
    else:
        form = MedicineForm(instance=medicine)
    
    return render(request, 'medicines/medicine_form.html', {
        'form': form,
        'medicine': medicine,
        'title': 'Edit Medicine'
    })

@login_required
@pharmacist_or_admin_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    
    if request.method == 'POST':
        medicine_name = medicine.name
        medicine.delete()
        messages.success(request, f'Medicine "{medicine_name}" deleted successfully!')
        return redirect('medicines:list')
    
    return render(request, 'medicines/medicine_confirm_delete.html', {'medicine': medicine})

@login_required
def stock_transactions(request):
    transactions = StockTransaction.objects.select_related('medicine', 'created_by').all()
    
    # Filter by medicine if specified
    medicine_id = request.GET.get('medicine')
    if medicine_id:
        transactions = transactions.filter(medicine_id=medicine_id)
    
    # Filter by transaction type
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Pagination
    paginator = Paginator(transactions, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'transaction_types': StockTransaction.TRANSACTION_TYPES,
        'medicines': Medicine.objects.filter(is_active=True),
    }
    return render(request, 'medicines/stock_transactions.html', context)

@login_required
@staff_or_above_required
def add_stock_transaction(request):
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.created_by = request.user
            transaction.save()
            messages.success(request, 'Stock transaction recorded successfully!')
            return redirect('medicines:transactions')
    else:
        form = StockTransactionForm()
        # Pre-select medicine if specified
        medicine_id = request.GET.get('medicine')
        if medicine_id:
            form.fields['medicine'].initial = medicine_id
    
    return render(request, 'medicines/transaction_form.html', {'form': form})

@login_required
def low_stock_alert(request):
    low_stock_medicines = Medicine.objects.filter(
        current_stock__lte=F('minimum_stock'),
        is_active=True
    ).select_related('category', 'supplier')
    
    context = {
        'medicines': low_stock_medicines,
        'count': low_stock_medicines.count(),
    }
    return render(request, 'medicines/low_stock_alert.html', context)

@login_required
def expiry_alert(request):
    today = timezone.now().date()
    thirty_days_later = today + timedelta(days=30)
    
    expired_medicines = Medicine.objects.filter(
        expiry_date__lt=today,
        is_active=True
    ).select_related('category', 'supplier')
    
    expiring_medicines = Medicine.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=thirty_days_later,
        is_active=True
    ).select_related('category', 'supplier')
    
    context = {
        'expired_medicines': expired_medicines,
        'expiring_medicines': expiring_medicines,
        'expired_count': expired_medicines.count(),
        'expiring_count': expiring_medicines.count(),
    }
    return render(request, 'medicines/expiry_alert.html', context)

# Category Views
@login_required
def category_list(request):
    categories = Category.objects.annotate(medicine_count=Count('medicines'))
    return render(request, 'medicines/category_list_new.html', {'categories': categories})

@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    medicines = Medicine.objects.filter(category=category)
    
    context = {
        'category': category,
        'medicines': medicines,
        'medicine_count': medicines.count()
    }
    return render(request, 'medicines/category_detail.html', context)

@login_required
@staff_or_above_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('medicines:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'medicines/category_form.html', {
        'form': form,
        'title': 'Add New Category'
    })

@login_required
@staff_or_above_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('medicines:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'medicines/category_form.html', {
        'form': form,
        'category': category,
        'title': 'Edit Category'
    })

@login_required
@staff_or_above_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    name = category.name
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully!')
        return redirect('medicines:category_list')
    
    return redirect('medicines:category_detail', pk=pk)

# Supplier Views
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.annotate(medicine_count=Count('medicines'))
    return render(request, 'medicines/supplier_list.html', {'suppliers': suppliers})

@login_required
@staff_or_above_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.name}" created successfully!')
            return redirect('medicines:supplier_list')
    else:
        form = SupplierForm()
    
    return render(request, 'medicines/supplier_form.html', {
        'form': form,
        'title': 'Add New Supplier'
    })

@login_required
@staff_or_above_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.name}" updated successfully!')
            return redirect('medicines:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'medicines/supplier_form.html', {
        'form': form,
        'supplier': supplier,
        'title': 'Edit Supplier'
    })

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    medicines = Medicine.objects.filter(supplier=supplier)
    
    context = {
        'supplier': supplier,
        'medicines': medicines,
        'medicine_count': medicines.count()
    }
    return render(request, 'medicines/supplier_detail.html', context)

# API Views
@login_required
def medicine_search_api(request):
    query = request.GET.get('q', '')
    medicines = Medicine.objects.filter(
        Q(name__icontains=query) |
        Q(generic_name__icontains=query) |
        Q(barcode__icontains=query),
        is_active=True
    )[:10]
    
    results = [{
        'id': medicine.id,
        'name': medicine.name,
        'generic_name': medicine.generic_name,
        'strength': medicine.strength,
        'current_stock': medicine.current_stock,
        'selling_price': str(medicine.selling_price),
    } for medicine in medicines]
    
    return JsonResponse({'results': results})

@login_required
def medicine_stock_api(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    return JsonResponse({
        'current_stock': medicine.current_stock,
        'minimum_stock': medicine.minimum_stock,
        'is_low_stock': medicine.is_low_stock,
        'stock_status': medicine.stock_status,
    })