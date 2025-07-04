from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, F, Q
from django.utils import timezone
from datetime import datetime, timedelta
from medicines.models import Medicine, StockTransaction, Category, Supplier, Alert
from accounts.models import UserProfile
from accounts.decorators import active_user_required

@login_required
@active_user_required
def home(request):
    # Basic statistics
    total_medicines = Medicine.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    total_suppliers = Supplier.objects.filter(is_active=True).count()
    
    # Stock statistics
    low_stock_count = Medicine.objects.filter(
        current_stock__lte=F('minimum_stock'),
        is_active=True
    ).count()
    
    out_of_stock_count = Medicine.objects.filter(
        current_stock=0,
        is_active=True
    ).count()
    
    # Expiry statistics
    today = timezone.now().date()
    thirty_days_later = today + timedelta(days=30)
    
    expired_count = Medicine.objects.filter(
        expiry_date__lt=today,
        is_active=True
    ).count()
    
    expiring_soon_count = Medicine.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=thirty_days_later,
        is_active=True
    ).count()
    
    # Recent transactions
    recent_transactions = StockTransaction.objects.select_related(
        'medicine', 'created_by'
    ).order_by('-created_at')[:10]
    
    # Top categories by medicine count
    top_categories = Category.objects.annotate(
        medicine_count=Count('medicines')
    ).order_by('-medicine_count')[:5]
    
    # Low stock medicines
    low_stock_medicines = Medicine.objects.filter(
        current_stock__lte=F('minimum_stock'),
        is_active=True
    ).select_related('category', 'supplier')[:5]
    
    # Expiring medicines
    expiring_medicines = Medicine.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=thirty_days_later,
        is_active=True
    ).select_related('category', 'supplier').order_by('expiry_date')[:5]
    
    # Monthly transaction summary (last 6 months)
    six_months_ago = today - timedelta(days=180)
    monthly_transactions = []
    
    for i in range(6):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        purchases = StockTransaction.objects.filter(
            transaction_type='purchase',
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        sales = StockTransaction.objects.filter(
            transaction_type='sale',
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        monthly_transactions.append({
            'month': month_start.strftime('%B %Y'),
            'purchases': purchases,
            'sales': sales
        })
    
    monthly_transactions.reverse()
    
    # Stock value calculation
    total_stock_value = Medicine.objects.filter(
        is_active=True
    ).aggregate(
        total_value=Sum(F('current_stock') * F('unit_price'))
    )['total_value'] or 0
    
    context = {
        'total_medicines': total_medicines,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'expired_count': expired_count,
        'expiring_soon_count': expiring_soon_count,
        'recent_transactions': recent_transactions,
        'top_categories': top_categories,
        'low_stock_medicines': low_stock_medicines,
        'expiring_medicines': expiring_medicines,
        'monthly_transactions': monthly_transactions,
        'total_stock_value': total_stock_value,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
@active_user_required
def analytics(request):
    # Stock distribution by category
    category_distribution = Category.objects.annotate(
        total_stock=Sum('medicines__current_stock'),
        medicine_count=Count('medicines')
    ).order_by('-total_stock')
    
    # Stock status distribution
    stock_status_data = {
        'normal': 0,
        'low_stock': 0,
        'out_of_stock': 0,
        'overstock': 0
    }
    
    medicines = Medicine.objects.filter(is_active=True)
    for medicine in medicines:
        stock_status_data[medicine.stock_status] += 1
    
    # Expiry status distribution
    today = timezone.now().date()
    thirty_days_later = today + timedelta(days=30)
    
    expiry_status_data = {
        'expired': Medicine.objects.filter(
            expiry_date__lt=today,
            is_active=True
        ).count(),
        'expiring_soon': Medicine.objects.filter(
            expiry_date__gte=today,
            expiry_date__lte=thirty_days_later,
            is_active=True
        ).count(),
        'valid': Medicine.objects.filter(
            expiry_date__gt=thirty_days_later,
            is_active=True
        ).count()
    }
    
    # Transaction trends (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    daily_transactions = []
    
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        
        purchases = StockTransaction.objects.filter(
            transaction_type='purchase',
            created_at__date=date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        sales = StockTransaction.objects.filter(
            transaction_type='sale',
            created_at__date=date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        daily_transactions.append({
            'date': date.strftime('%Y-%m-%d'),
            'purchases': purchases,
            'sales': sales
        })
    
    # Top suppliers by medicine count
    top_suppliers = Supplier.objects.filter(
        is_active=True
    ).annotate(
        medicine_count=Count('medicines'),
        total_stock=Sum('medicines__current_stock')
    ).order_by('-medicine_count')[:10]
    
    # Most active users (by transactions)
    active_users = UserProfile.objects.filter(
        user__stocktransaction_created_by__created_at__gte=thirty_days_ago
    ).annotate(
        transaction_count=Count('user__stocktransaction_created_by')
    ).order_by('-transaction_count')[:5]
    
    context = {
        'category_distribution': category_distribution,
        'stock_status_data': stock_status_data,
        'expiry_status_data': expiry_status_data,
        'daily_transactions': daily_transactions,
        'top_suppliers': top_suppliers,
        'active_users': active_users,
    }
    
    return render(request, 'dashboard/analytics.html', context)

@login_required
@active_user_required
def reports(request):
    # Generate various reports based on request parameters
    report_type = request.GET.get('type', 'stock')
    
    context = {'report_type': report_type}
    
    if report_type == 'stock':
        # Stock report
        medicines = Medicine.objects.filter(
            is_active=True
        ).select_related('category', 'supplier').order_by('name')
        
        context.update({
            'medicines': medicines,
            'total_medicines': medicines.count(),
            'total_stock_value': sum(
                medicine.current_stock * medicine.unit_price 
                for medicine in medicines
            )
        })
    
    elif report_type == 'low_stock':
        # Low stock report
        low_stock_medicines = Medicine.objects.filter(
            current_stock__lte=F('minimum_stock'),
            is_active=True
        ).select_related('category', 'supplier')
        
        context.update({
            'medicines': low_stock_medicines,
            'total_medicines': low_stock_medicines.count()
        })
    
    elif report_type == 'expiry':
        # Expiry report
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
        
        context.update({
            'expired_medicines': expired_medicines,
            'expiring_medicines': expiring_medicines,
            'expired_count': expired_medicines.count(),
            'expiring_count': expiring_medicines.count()
        })
    
    elif report_type == 'transactions':
        # Transaction report
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        transactions = StockTransaction.objects.select_related(
            'medicine', 'created_by'
        ).order_by('-created_at')
        
        if date_from:
            transactions = transactions.filter(
                created_at__date__gte=datetime.strptime(date_from, '%Y-%m-%d').date()
            )
        
        if date_to:
            transactions = transactions.filter(
                created_at__date__lte=datetime.strptime(date_to, '%Y-%m-%d').date()
            )
        
        context.update({
            'transactions': transactions[:100],  # Limit to 100 for performance
            'total_transactions': transactions.count(),
            'date_from': date_from,
            'date_to': date_to
        })
    
    return render(request, 'dashboard/reports.html', context)