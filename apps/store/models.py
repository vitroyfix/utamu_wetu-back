from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self): return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self): return self.name

class Weight(models.Model):
    value = models.CharField(max_length=20) 
    unit = models.CharField(max_length=10, default="g")
    def __str__(self): return f"{self.value} {self.unit}"

class Product(models.Model):
    # 1) Product Identity (Core Data)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, null=True, help_text="Product ID (SKU)")
    barcode = models.CharField(max_length=13, null=True, blank=True, help_text="EAN/Barcode")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    subcategory = models.CharField(max_length=100, null=True, blank=True)
    product_type = models.CharField(max_length=100, null=True, blank=True, help_text="e.g. Perishable beverage")
    
    # 2) Commercial Information
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    packaging_type = models.CharField(max_length=100, null=True, blank=True, help_text="e.g. Carton")
    min_order = models.PositiveIntegerField(default=1)
    max_order = models.PositiveIntegerField(default=12, help_text="Value in units (Logic will convert to Dozens in Frontend)")
    packaging_image = models.ImageField(upload_to='products/technical/', null=True, blank=True, help_text="Visual brand & size verification image.")
    nutrition_image = models.ImageField(upload_to='products/technical/', null=True, blank=True, help_text="Verified facts & certifications image.")
    description = models.TextField(help_text="Detailed explanation of origin, processing, and use.")
    ingredients = models.TextField(null=True, blank=True)
    nutritional_info = models.TextField(null=True, blank=True, help_text="Enter nutrition facts as plain text.")
    storage_instructions = models.TextField(null=True, blank=True)
    shelf_life = models.CharField(max_length=100, null=True, blank=True)
    expiry_info = models.CharField(max_length=255, null=True, blank=True, help_text="e.g. Printed on package")
    country_of_origin = models.CharField(max_length=100, default="Kenya")
    allergens = models.TextField(null=True, blank=True, help_text="e.g. Contains Milk")
    manufacturer = models.CharField(max_length=200, null=True, blank=True)
    processing_method = models.CharField(max_length=100, null=True, blank=True, help_text="e.g. Pasteurized")
    quality_certification = models.CharField(max_length=200, default="KEBS certified")
    requires_cold_transport = models.BooleanField(default=False)
    same_day_delivery = models.BooleanField(default=True)
    weight = models.ForeignKey(Weight, on_delete=models.SET_NULL, null=True, related_name='products')
    tags = models.ManyToManyField(Tag, blank=True)
    is_popular = models.BooleanField(default=False)
    is_hot_deal = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False) 
    total_stock = models.PositiveIntegerField(default=100) 
    sold_count = models.PositiveIntegerField(default=0)    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self): return self.title

    @property
    def stock_available(self):
        return max(0, self.total_stock - self.sold_count)

    @property
    def discount_percentage(self):
        if self.old_price and self.old_price > self.price:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return round(discount)
        return 0

class ProductImage(models.Model):
    """Standard gallery images for the top slider."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.product.title} - Gallery Image"

class Showcase(models.Model):
    title = models.CharField(max_length=100, help_text="e.g., Summer Refreshments")
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='showcase/')
    link_url = models.CharField(max_length=255, blank=True, help_text="e.g., /shop/fruits")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title