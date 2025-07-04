from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'phone_number', 'address', 'date_of_birth', 'profile_picture', 'is_active')

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_is_active', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'userprofile__role', 'userprofile__is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    def get_role(self, obj):
        return obj.userprofile.get_role_display() if hasattr(obj, 'userprofile') else 'No Profile'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'userprofile__role'
    
    def get_is_active(self, obj):
        return obj.userprofile.is_active if hasattr(obj, 'userprofile') else obj.is_active
    get_is_active.short_description = 'Profile Active'
    get_is_active.boolean = True
    get_is_active.admin_order_field = 'userprofile__is_active'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'profile_picture')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)