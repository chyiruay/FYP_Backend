from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Donation, CustomUser, Category, Location, DonationHistory, Shelter
# Register CustomUser with default UserAdmin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = [
        'id', 'username', 'email', 'last_login', 'date_joined', 'is_staff', 'is_active', 'is_employee'
    ]
    list_filter = ['is_staff', 'is_active', 'is_employee']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': (
                'is_employee',
                'phone_number',
                'gender',
                'house_number',
                'street_name',
                'residential_area',
                'postcode',
                'city',
                'state',
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': (
                'is_employee',
                'phone_number',
                'gender',
                'house_number',
                'street_name',
                'residential_area',
                'postcode',
                'city',
                'state',
            )
        }),
    )
    
admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Donation)
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(DonationHistory)
admin.site.register(Shelter)

