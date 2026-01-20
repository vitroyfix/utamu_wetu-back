import graphene
from graphene_django import DjangoObjectType
from .models import Product, Category, Brand, Tag, Weight, ProductImage, Showcase

# --- 1. Object Types ---

class ShowcaseType(DjangoObjectType):
    """Independent lifestyle/marketing assets for the frontend showcase."""
    class Meta:
        model = Showcase
        # ADDED: 'is_active' must be here to be queried as 'isActive' in GraphQL
        fields = ("id", "title", "subtitle", "image", "link_url", "is_active")

    def resolve_image(self, info):
        """Builds absolute URL so port 3000 can see images from port 8000."""
        if self.image:
            return info.context.build_absolute_uri(self.image.url)
        return None

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "image")

    def resolve_image(self, info):
        if self.image:
            return info.context.build_absolute_uri(self.image.url)
        return None

class BrandType(DjangoObjectType):
    class Meta:
        model = Brand
        fields = ("id", "name")

class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = ("id", "name")

class WeightType(DjangoObjectType):
    class Meta:
        model = Weight
        fields = ("id", "value", "unit")

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

    class Meta:
        model = Product
        fields = "__all__"

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
    
    popular_products = graphene.List(ProductType, category_name=graphene.String())
    deals_of_the_day = graphene.List(ProductType)
    daily_best_sells = graphene.List(ProductType)
    product_by_id = graphene.Field(ProductType, id=graphene.ID(required=True))

    # --- Resolvers ---

    def resolve_all_categories(root, info):
        return Category.objects.all()

    def resolve_all_brands(root, info):
        return Brand.objects.all()

    def resolve_all_tags(root, info):
        return Tag.objects.all()

    def resolve_all_showcases(root, info):
        """Fetches active marketing assets. Added ordering to ensure consistent UI."""
        return Showcase.objects.filter(is_active=True).order_by('order')

    def resolve_popular_products(root, info, category_name=None):
        # Optimization: select_related for ForeignKeys, prefetch_related for ManyToMany/Reverse FK
        queryset = Product.objects.select_related('weight', 'brand', 'category').filter(is_popular=True)
        if category_name and category_name != "All":
            queryset = queryset.filter(category__name__iexact=category_name)
        return queryset.prefetch_related('tags', 'images')

    def resolve_deals_of_the_day(root, info):
        return Product.objects.select_related('weight', 'brand', 'category').filter(is_hot_deal=True)[:4].prefetch_related('images')

    def resolve_daily_best_sells(root, info):
        return Product.objects.select_related('weight', 'brand', 'category').filter(is_popular=True).order_by('-created_at')[:8].prefetch_related('images')

    def resolve_product_by_id(root, info, id):
        try:
            return Product.objects.prefetch_related('images', 'tags').get(pk=id)
        except Product.DoesNotExist:
            return None

# --- 3. Schema Initialization ---

schema = graphene.Schema(query=Query)