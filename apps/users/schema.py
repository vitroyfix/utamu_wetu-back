import graphene
import graphql_jwt
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
from .models import UserProfile, Address, Voucher, VoucherUsage
from django.utils import timezone
from graphql_jwt.decorators import login_required

# --- Types ---

class UserProfileType(DjangoObjectType):
    class Meta:
        model = UserProfile
        fields = ("id", "avatar", "bio", "coins", "is_subscribed", "created_at")

class AddressType(DjangoObjectType):
    class Meta:
        model = Address
        fields = ("id", "full_name", "phone_number", "county", "estate", "house_number", "street_address", "is_default", "address_type")

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "profile", "addresses")

class VoucherType(DjangoObjectType):
    is_valid_now = graphene.Boolean()

    class Meta:
        model = Voucher
        fields = ("id", "code", "discount_amount", "is_percentage", "min_purchase_amount", "valid_to")

    def resolve_is_valid_now(self, info):
        return self.is_valid

# --- Custom JWT Mutation ---

class CustomObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    """
    Customizes the tokenAuth response to include the user object.
    """
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)

# --- Query ---

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    my_addresses = graphene.List(AddressType)
    check_voucher = graphene.Field(VoucherType, code=graphene.String(required=True))
    user_detail = graphene.Field(UserType, username=graphene.String(required=True))
    user_vouchers = graphene.List(VoucherType, username=graphene.String(required=True))

    @login_required
    def resolve_me(self, info):
        return info.context.user

    @login_required
    def resolve_my_addresses(self, info):
        return Address.objects.filter(user=info.context.user)

    def resolve_check_voucher(self, info, code):
        try:
            voucher = Voucher.objects.get(code__iexact=code, active=True)
            return voucher if voucher.is_valid else None
        except Voucher.DoesNotExist:
            return None

    def resolve_user_detail(self, info, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def resolve_user_vouchers(self, info, username):
        return Voucher.objects.filter(voucherusage__user__username=username)

# --- Mutations ---

class UpdateProfileMutation(graphene.Mutation):
    class Arguments:
        bio = graphene.String()
        is_subscribed = graphene.Boolean()

    success = graphene.Boolean()
    profile = graphene.Field(UserProfileType)

    @login_required
    def mutate(self, info, bio=None, is_subscribed=None):
        profile = info.context.user.profile
        if bio is not None:
            profile.bio = bio
        if is_subscribed is not None:
            profile.is_subscribed = is_subscribed
        profile.save()
        return UpdateProfileMutation(success=True, profile=profile)

class CreateAddressMutation(graphene.Mutation):
    class Arguments:
        full_name = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        county = graphene.String()
        estate = graphene.String(required=True)
        house_number = graphene.String(required=True)
        street_address = graphene.String()
        is_default = graphene.Boolean()
        address_type = graphene.String()

    address = graphene.Field(AddressType)

    @login_required
    def mutate(self, info, **kwargs):
        address = Address.objects.create(user=info.context.user, **kwargs)
        return CreateAddressMutation(address=address)

class Mutation(graphene.ObjectType):
    update_profile = UpdateProfileMutation.Field()
    create_address = CreateAddressMutation.Field()