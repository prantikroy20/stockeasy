from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import (
    CustomUserCreationForm, 
    UserProfileForm, 
    UserUpdateForm,
    AdminUserCreationForm
)
from .models import UserProfile
from .decorators import admin_required

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    user_form = UserUpdateForm(instance=request.user)
    profile_form = UserProfileForm(instance=request.user.userprofile)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, 
            request.FILES, 
            instance=request.user.userprofile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/profile.html', context)

@login_required
@admin_required
def user_management(request):
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    users = User.objects.select_related('userprofile').all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if role_filter:
        users = users.filter(userprofile__role=role_filter)
    
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'role_choices': UserProfile.ROLE_CHOICES,
    }
    return render(request, 'accounts/user_management.html', context)

@login_required
@admin_required
def create_user(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('accounts:user_management')
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'accounts/create_user.html', {'form': form})

@login_required
@admin_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.userprofile
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        role = request.POST.get('role')
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            if role:
                profile.role = role
                profile.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('accounts:user_management')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_obj': user,
        'role_choices': UserProfile.ROLE_CHOICES,
        'current_role': profile.role,
    }
    return render(request, 'accounts/edit_user.html', context)

@login_required
@admin_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.userprofile
    
    if user != request.user:  # Prevent admin from deactivating themselves
        profile.is_active = not profile.is_active
        user.is_active = profile.is_active
        profile.save()
        user.save()
        
        status = "activated" if profile.is_active else "deactivated"
        messages.success(request, f'User {user.username} has been {status}.')
    else:
        messages.error(request, 'You cannot deactivate your own account.')
    
    return redirect('accounts:user_management')

@login_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Check if user has permission to view other users' details
    if not request.user.userprofile.can_manage_users() and user != request.user:
        messages.error(request, 'You do not have permission to view this user.')
        return redirect('dashboard:home')
    
    context = {'user_obj': user}
    return render(request, 'accounts/user_detail.html', context)