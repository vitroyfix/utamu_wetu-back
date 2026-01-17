from django.contrib import admin
from .models import Category, Brand, Tag, Weight, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'is_popular', 'is_hot_deal', 'created_at')
    list_filter = ('category', 'brand', 'is_popular', 'is_hot_deal')
    search_fields = ('title', 'description')
    inlines = [ProductImageInline]

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Tag)
admin.site.register(Weight)