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
    def __str__(self): return self.value

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    available_weights = models.ManyToManyField(Weight, blank=True)
    is_popular = models.BooleanField(default=False)
    is_hot_deal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.title

class ProductImage(models.Model):
    # For multiple thumbnails (Gallery)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')