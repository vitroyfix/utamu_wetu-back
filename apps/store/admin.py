from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category, Brand, Tag, Weight, Product, ProductImage, Showcase


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" height="80" style="object-fit: cover; border-radius: 5px;" />')
        return "No Image"

@admin.register(Showcase)
class ShowcaseAdmin(admin.ModelAdmin):
    list_display = ('showcase_preview', 'title', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle')
    
    readonly_fields = ('showcase_preview',)
    fields = ('title', 'subtitle', 'image', 'showcase_preview', 'link_url', 'is_active', 'order')

    def showcase_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150" style="object-fit: contain; border-radius: 8px; border: 1px solid #eee;" />')
        return "No Image Uploaded"
    
    showcase_preview.short_description = 'Current Image'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'get_main_image', 'title', 'category', 'price', 
        'is_best_seller', 'sold_count', 'total_stock', 'discount_display'
    )
    
    list_editable = ('is_best_seller', 'sold_count', 'total_stock')
    list_filter = ('category', 'brand', 'is_popular', 'is_hot_deal', 'is_best_seller')
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title",)}
    
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('General Information', {
            'fields': ('title', 'slug', 'description', 'category', 'brand', 'weight', 'tags')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'old_price', 'total_stock', 'sold_count')
        }),
        ('Status & Promotions', {
            'fields': ('is_popular', 'is_hot_deal', 'is_best_seller')
        }),
    )

    def get_main_image(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return mark_safe(f'<img src="{first_image.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />')
        return "N/A"
    
    get_main_image.short_description = 'Preview'

    def discount_display(self, obj):
        if obj.discount_percentage > 0:
            return mark_safe(f'<b style="color: #3BB77E;">{obj.discount_percentage}% Off</b>')
        return "No Discount"
    discount_display.short_description = 'Savings'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('images')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_image', 'name', 'slug')
    prepopulated_fields = {"slug": ("name",)}
    
    def category_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="40" height="40" style="border-radius: 50%;" />')
        return "N/A"

@admin.register(Weight)
class WeightAdmin(admin.ModelAdmin):
    list_display = ('value', 'unit')
    list_filter = ('unit',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)