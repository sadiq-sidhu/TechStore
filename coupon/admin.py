from django.contrib import admin
from .models import Coupon, CouponUsage

class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'min_purchase_amount', 'valid_from', 'valid_to', 'coupon_type', 'is_active')
    list_filter = ('is_active', 'coupon_type', 'valid_from', 'valid_to')
    search_fields = ('code',)
    readonly_fields = ('valid_from', 'valid_to')
    fieldsets = (
        ('Coupon Information', {
            'fields': ('code', 'discount_amount', 'min_purchase_amount', 'coupon_type', 'is_active')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to')
        }),
    )

admin.site.register(Coupon, CouponAdmin)

class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'coupon', 'used_at')
    list_filter = ('coupon', 'used_at')
    search_fields = ('user__username', 'coupon__code')

admin.site.register(CouponUsage, CouponUsageAdmin)

