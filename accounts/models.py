from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('pharmacist', 'Pharmacist'),
        ('staff', 'Staff Member'),
        ('viewer', 'Viewer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip()
    
    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        permissions = {
            'admin': ['view', 'add', 'edit', 'delete', 'manage_users'],
            'pharmacist': ['view', 'add', 'edit', 'delete'],
            'staff': ['view', 'add', 'edit'],
            'viewer': ['view'],
        }
        return permission in permissions.get(self.role, [])
    
    def can_manage_users(self):
        return self.role == 'admin'
    
    def can_delete_medicines(self):
        return self.role in ['admin', 'pharmacist']
    
    def can_edit_medicines(self):
        return self.role in ['admin', 'pharmacist', 'staff']
    
    def can_view_medicines(self):
        return True  # All authenticated users can view