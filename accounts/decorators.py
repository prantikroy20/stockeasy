from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            user_role = getattr(request.user.userprofile, 'role', None)
            if user_role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard:home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """Decorator to check if user is admin"""
    return role_required(['admin'])(view_func)

def pharmacist_or_admin_required(view_func):
    """Decorator to check if user is pharmacist or admin"""
    return role_required(['admin', 'pharmacist'])(view_func)

def staff_or_above_required(view_func):
    """Decorator to check if user is staff, pharmacist, or admin"""
    return role_required(['admin', 'pharmacist', 'staff'])(view_func)

def permission_required(permission):
    """Decorator to check specific permission"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if not request.user.userprofile.has_permission(permission):
                messages.error(request, 'You do not have permission to perform this action.')
                return redirect('dashboard:home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def active_user_required(view_func):
    """Decorator to check if user account is active"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if not request.user.userprofile.is_active:
            messages.error(request, 'Your account has been deactivated. Please contact an administrator.')
            return redirect('accounts:login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view