from django.contrib import admin
from .models import Order, OrderItem, TrackingHistory

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price_at_purchase', 'total_item_price')
    fields = ('product', 'quantity', 'price_at_purchase', 'total_item_price')

    def total_item_price(self, obj):
        return obj.total_item_price
    total_item_price.short_description = 'Subtotal'

class TrackingHistoryInline(admin.TabularInline):
    model = TrackingHistory
    extra = 1  #
    fields = ('status', 'location', 'message', 'timestamp')
    readonly_fields = ('timestamp',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 
        'user', 
        'total_amount', 
        'payment_status', 
        'delivery_status', 
        'created_at'
    )
    list_filter = ('payment_status', 'delivery_status', 'created_at')
    search_fields = ('order_number', 'user__username', 'transaction_id')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
   
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'total_amount', 'transaction_id')
        }),
        ('Status', {
            'fields': ('payment_status', 'delivery_status', 'tracking_number')
        }),
        ('Logistics', {
            'fields': ('shipping_address',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [OrderItemInline, TrackingHistoryInline]

@admin.register(TrackingHistory)
class TrackingHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'location', 'timestamp')
    list_filter = ('status', 'timestamp')