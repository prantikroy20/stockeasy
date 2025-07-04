from django.urls import path
from . import views

app_name = 'medicines'

urlpatterns = [
    # Medicine URLs
    path('', views.medicine_list, name='list'),
    path('<int:pk>/', views.medicine_detail, name='detail'),
    path('create/', views.medicine_create, name='create'),
    path('<int:pk>/edit/', views.medicine_update, name='update'),
    path('<int:pk>/delete/', views.medicine_delete, name='delete'),
    
    # Stock Transaction URLs
    path('transactions/', views.stock_transactions, name='transactions'),
    path('transactions/add/', views.add_stock_transaction, name='add_transaction'),
    
    # Alert URLs
    path('alerts/low-stock/', views.low_stock_alert, name='low_stock_alert'),
    path('alerts/expiry/', views.expiry_alert, name='expiry_alert'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Supplier URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_update, name='supplier_update'),
    
    # API URLs
    path('api/search/', views.medicine_search_api, name='search_api'),
    path('api/<int:pk>/stock/', views.medicine_stock_api, name='stock_api'),
]