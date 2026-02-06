import graphene
from graphene_django import DjangoObjectType
from django.db.models import Max, Q
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
    name = graphene.String()
    stock_available = graphene.Int()
    old_price = graphene.Float()
    sold_count = graphene.Int()

    class Meta:
        model = Product
        # SYNCED: Added barcode, product_type, max_order, requires_cold_transport, and packaging_type
        fields = (
            "id", "title", "price", "description", "slug", 
            "total_stock", "is_popular", "is_hot_deal", 
            "is_best_seller", "weight", "brand", "category", 
            "images", "tags", "packaging_image", "nutrition_image",
            "nutritional_info", "stock_available", "old_price", 
            "sold_count", "sku", "ingredients", "allergens",
            "storage_instructions", "manufacturer", "country_of_origin",
            "barcode", "product_type", "max_order", "requires_cold_transport", "packaging_type"
        )

    def resolve_name(self, info):
        return self.title

    def resolve_stock_available(self, info):
        # Maps the frontend field to your total_stock data
        return self.total_stock

    def resolve_old_price(self, info):
        return getattr(self, 'old_price', 0.0)

    def resolve_sold_count(self, info):
        return getattr(self, 'sold_count', 0)

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

# --- 2. Mutations ---

class CreateCategoryMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    category = graphene.Field(CategoryType)

    def mutate(self, info, name):
        category = Category.objects.create(name=name)
        return CreateCategoryMutation(category=category)

class CreateProductMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        price = graphene.Float(required=True)
        category_id = graphene.Int(required=True)
        description = graphene.String()
        total_stock = graphene.Int()
        is_popular = graphene.Boolean()
        is_hot_deal = graphene.Boolean()
        is_best_seller = graphene.Boolean()

    product = graphene.Field(ProductType)

    def mutate(self, info, **kwargs):
        try:
            category_id = kwargs.pop('category_id')
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise Exception("Category not found.")

        product = Product.objects.create(category=category, **kwargs)
        return CreateProductMutation(product=product)

class Mutation(graphene.ObjectType):
    create_category = CreateCategoryMutation.Field()
    create_product = CreateProductMutation.Field()

# --- 3. Query Class ---

class Query(graphene.ObjectType):
    all_categories = graphene.List(CategoryType)
    all_brands = graphene.List(BrandType)
    all_tags = graphene.List(TagType)
    all_showcases = graphene.List(ShowcaseType)
    all_weights = graphene.List(WeightType)
    
    all_products = graphene.List(
        ProductType, 
        search=graphene.String(),
        category_name=graphene.String(),
        tag_name=graphene.String(),
        min_price=graphene.Float(),
        max_price=graphene.Float()
    )
    
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

    def resolve_all_products(root, info, search=None, category_name=None, **kwargs):
        queryset = Product.objects.all()
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
        if category_name and category_name != "All":
            queryset = queryset.filter(category__name__iexact=category_name)
        return queryset.prefetch_related('tags', 'images')

    def resolve_all_brands(root, info):
        return Brand.objects.all()

    def resolve_all_tags(root, info):
        return Tag.objects.all()
    
    def resolve_all_weights(root, info):
        return Weight.objects.all()

    def resolve_all_showcases(root, info):
        return Showcase.objects.filter(is_active=True).order_by('order')

    def resolve_popular_products(root, info, category_name=None, **kwargs):
        queryset = Product.objects.filter(is_popular=True)
        if category_name and category_name != "All":
            queryset = queryset.filter(category__name__iexact=category_name)
        return queryset.prefetch_related('tags', 'images')

    def resolve_deals_of_the_day(root, info):
        return Product.objects.filter(is_hot_deal=True)[:4].prefetch_related('images')

    def resolve_daily_best_sells(root, info):
        return Product.objects.filter(is_best_seller=True).order_by('-created_at')[:8].prefetch_related('images')

    def resolve_product_by_id(root, info, id):
        try:
            return Product.objects.prefetch_related('images', 'tags').get(pk=id)
        except Product.DoesNotExist:
            return None

    # REFINED: Added iexact and strip to fix the "Product not found" issue
    def resolve_product_by_slug(root, info, slug):
        try:
            clean_slug = slug.strip("/")
            return Product.objects.select_related('weight', 'brand', 'category').prefetch_related('images', 'tags').get(slug__iexact=clean_slug)
        except Product.DoesNotExist:
            return None

# --- 4. Schema Initialization ---
schema = graphene.Schema(query=Query, mutation=Mutation)