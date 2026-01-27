import graphene
from graphene_django import DjangoObjectType
from django.db.models import Max, Count 
from .models import Product, Category, Brand, Tag, Weight, ProductImage, Showcase

# --- 1. Object Types ---

class ShowcaseType(DjangoObjectType):
    class Meta:
        model = Showcase
        fields = ("id", "title", "subtitle", "image", "link_url", "is_active")

    def resolve_image(self, info):
        if self.image:
            return info.context.build_absolute_uri(self.image.url)
        return None

class CategoryType(DjangoObjectType):
    max_price = graphene.Float()
    product_count = graphene.Int()

    class Meta:
        model = Category
        fields = ("id", "name", "image", "slug")

    def resolve_image(self, info):
        if self.image:
            return info.context.build_absolute_uri(self.image.url)
        return None

    def resolve_max_price(self, info):
        max_val = Product.objects.filter(category=self).aggregate(Max('price'))['price__max']
        return max_val if max_val else 0.0

    def resolve_product_count(self, info):
        return Product.objects.filter(category=self).count()

class BrandType(DjangoObjectType):
    class Meta:
        model = Brand
        fields = ("id", "name")

class TagType(DjangoObjectType):
  
    product_count = graphene.Int()

    class Meta:
        model = Tag
        fields = ("id", "name")
    
    def resolve_product_count(self, info):
        return Product.objects.filter(tags=self).count()

class WeightType(DjangoObjectType):
    product_count = graphene.Int()

    class Meta:
        model = Weight
        fields = ("id", "value", "unit")
    
    def resolve_product_count(self, info):
        return Product.objects.filter(weight=self).count()

class ProductImageType(DjangoObjectType):
    class Meta:
        model = ProductImage
        fields = ("id", "image", "alt_text")

    def resolve_image(self, info):
        if self.image:
            return info.context.build_absolute_uri(self.image.url)
        return None

class ProductType(DjangoObjectType):
    weight = graphene.Field(WeightType)
    brand = graphene.Field(BrandType)
    category = graphene.Field(CategoryType)
    images = graphene.List(ProductImageType)
    tags = graphene.List(TagType)
    
    nutritional_info = graphene.String()

    class Meta:
        model = Product
        fields = "__all__"

    def resolve_packaging_image(self, info):
        if self.packaging_image:
            return info.context.build_absolute_uri(self.packaging_image.url)
        return None

    def resolve_nutrition_image(self, info):
        if self.nutrition_image:
            return info.context.build_absolute_uri(self.nutrition_image.url)
        return None

    def resolve_images(self, info):
        return self.images.all()

    def resolve_tags(self, info):
        return self.tags.all()

# --- 2. Query Class ---

class Query(graphene.ObjectType):
    all_categories = graphene.List(CategoryType)
    all_brands = graphene.List(BrandType)
    all_tags = graphene.List(TagType)
    all_showcases = graphene.List(ShowcaseType)
    all_weights = graphene.List(WeightType)
    popular_products = graphene.List(
        ProductType, 
        category_name=graphene.String(),
        tag_name=graphene.String(),
        min_price=graphene.Float(),
        max_price=graphene.Float()
    )
    deals_of_the_day = graphene.List(ProductType)
    daily_best_sells = graphene.List(ProductType)
    product_by_id = graphene.Field(ProductType, id=graphene.ID(required=True))
    product_by_slug = graphene.Field(ProductType, slug=graphene.String(required=True))

    def resolve_all_categories(root, info):
        return Category.objects.all()

    def resolve_all_brands(root, info):
        return Brand.objects.all()

    def resolve_all_tags(root, info):
        return Tag.objects.all()
    
    def resolve_all_weights(root, info):
        return Weight.objects.all()

    def resolve_all_showcases(root, info):
        return Showcase.objects.filter(is_active=True).order_by('order')

    def resolve_popular_products(root, info, category_name=None, tag_name=None, min_price=None, max_price=None):
        queryset = Product.objects.select_related('weight', 'brand', 'category').filter(is_popular=True)
        
        if category_name and category_name != "All":
            queryset = queryset.filter(category__name__iexact=category_name)

        if tag_name:
            queryset = queryset.filter(tags__name__iexact=tag_name)
        
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
            
        return queryset.prefetch_related('tags', 'images')

    def resolve_deals_of_the_day(root, info):
        return Product.objects.select_related('weight', 'brand', 'category').filter(is_hot_deal=True)[:4].prefetch_related('images')

    def resolve_daily_best_sells(root, info):
        return Product.objects.select_related('weight', 'brand', 'category').filter(is_best_seller=True).order_by('-created_at')[:8].prefetch_related('images')

    def resolve_product_by_id(root, info, id):
        try:
            return Product.objects.prefetch_related('images', 'tags').get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_product_by_slug(root, info, slug):
        try:
            return Product.objects.select_related('weight', 'brand', 'category').prefetch_related('images', 'tags').get(slug=slug)
        except Product.DoesNotExist:
            return None

# --- 3. Schema Initialization ---
schema = graphene.Schema(query=Query)