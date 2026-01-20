from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
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
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    weight = models.ForeignKey(Weight, on_delete=models.SET_NULL, null=True, related_name='products')
    tags = models.ManyToManyField(Tag, blank=True)
    is_popular = models.BooleanField(default=False)
    is_hot_deal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, null=True, blank=True)

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