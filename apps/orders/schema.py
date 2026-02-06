import graphene
import json
from graphene_django import DjangoObjectType
from .models import Order, OrderItem, TrackingHistory
from apps.store.models import Product
from apps.users.models import Address
from graphql_jwt.decorators import login_required

# --- Types ---

class OrderItemType(DjangoObjectType):
    total_item_price = graphene.Float()

    class Meta:
        model = OrderItem
        fields = ("id", "product", "price_at_purchase", "quantity", "total_item_price")

    def resolve_total_item_price(self, info):
        return self.total_item_price

class TrackingHistoryType(DjangoObjectType):
    class Meta:
        model = TrackingHistory
        fields = ("id", "status", "location", "message", "timestamp")

class OrderType(DjangoObjectType):
    # SYNC: These match the frontend query fields exactly
    payment_status_display = graphene.String()
    delivery_status_display = graphene.String()

    class Meta:
        model = Order
        fields = (
            "id", "order_number", "total_amount", "transaction_id", 
            "payment_status", "delivery_status", "tracking_number", 
            "created_at", "shipping_address", "items", "tracking_updates"
        )

    def resolve_payment_status_display(self, info):
        # Maps the human-readable Choice name from Django
        return self.get_payment_status_display()

    def resolve_delivery_status_display(self, info):
        # Maps the human-readable Choice name from Django
        return self.get_delivery_status_display()

# --- Mutations ---

class CreateOrderMutation(graphene.Mutation):
    class Arguments:
        # SYNC: Use ID for address_id as specified in your CREATE_ORDER mutation
        address_id = graphene.ID(required=True)
        items_json = graphene.String(required=True)

    order = graphene.Field(OrderType)
    success = graphene.Boolean()

    @login_required
    def mutate(self, info, address_id, items_json):
        user = info.context.user
        
        # 1. Validate Address
        try:
            shipping_address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            raise Exception("Shipping address not found.")

        # 2. Parse Items
        try:
            items_data = json.loads(items_json)
        except json.JSONDecodeError:
            raise Exception("Invalid items JSON format.")
        
        # Create initial order
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            total_amount=0 
        )

        running_total = 0
        for item in items_data:
            try:
                # SYNC: Frontend sends 'id' and 'qty'
                product = Product.objects.get(id=item['id'])
                qty = int(item['qty'])
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price_at_purchase=product.price
                )
                running_total += (product.price * qty)
            except (Product.DoesNotExist, KeyError, ValueError):
                continue # Or handle as a specific error

        # 3. Finalize Order
        order.total_amount = running_total
        order.save()

        return CreateOrderMutation(order=order, success=True)

# --- Combined Query and Mutation ---

class Query(graphene.ObjectType):
    my_orders = graphene.List(OrderType)
    # SYNC: Added for GET_ORDER_DETAILS
    order_by_number = graphene.Field(OrderType, order_number=graphene.String(required=True))
    
    @login_required
    def resolve_my_orders(self, info):
        return Order.objects.filter(user=info.context.user).order_by('-created_at')

    @login_required
    def resolve_order_by_number(self, info, order_number):
        try:
            return Order.objects.get(user=info.context.user, order_number=order_number)
        except Order.DoesNotExist:
            return None

class Mutation(graphene.ObjectType):
    create_order = CreateOrderMutation.Field()