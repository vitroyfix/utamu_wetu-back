from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, Address, Voucher, VoucherUsage

class AddressInline(admin.StackedInline):
    model = Address
    extra = 0
    fieldsets = (
        (None, {
           
            'fields': (('full_name', 'phone_number'), ('county', 'estate', 'house_number'), 'is_default', 'address_type')
        }),
    )


class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Info'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, AddressInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_coins', 'is_staff')
    
    def get_coins(self, instance):
        return instance.profile.coins
    get_coins.short_description = 'Loyalty Coins'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'estate', 'county', 'is_default', 'address_type')
    list_filter = ('county', 'address_type', 'is_default')
    search_fields = ('full_name', 'phone_number', 'estate')

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'is_percentage', 'min_purchase_amount', 'valid_to', 'active', 'is_currently_valid')
    list_filter = ('active', 'is_percentage', 'valid_to')
    search_fields = ('code',)
    readonly_fields = ('is_currently_valid',)

    def is_currently_valid(self, obj):
        return obj.is_valid
    is_currently_valid.boolean = True
    is_currently_valid.short_description = 'Valid Now?'

@admin.register(VoucherUsage)
class VoucherUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'voucher', 'used_at')
    list_filter = ('used_at', 'voucher')
    search_fields = ('user__username', 'voucher__code')
    readonly_fields = ('used_at',)