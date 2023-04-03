from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin 
from .forms import *
# Register your models here.
admin.site.register(Record)
admin.site.register(Leave)
class CustomUserAdmin(UserAdmin):  
    add_form = UserCreationForm  
    form = UserChangeForm  
    model = User  
  
    list_display = ('email', 'is_staff', 'is_active','first_name','last_name','Employee_id','Manager',)  
    list_filter = ('email', 'is_staff', 'is_active',)  
    fieldsets = ((None, {'fields': ('email', 'password','first_name','last_name','phone_number','Medical_leave','Personal_leave','Manager')}),  
        ('Permissions', {'fields': ('is_staff', 'is_active','is_superuser')}),)  
    add_fieldsets = ((None, {'classes': ('wide',),  
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active','first_name','last_name','Employee_id','Manager')}),)  
    search_fields = ('email',)  
    ordering = ('email',)  
    filter_horizontal = ()  
  
admin.site.register(User, CustomUserAdmin)  