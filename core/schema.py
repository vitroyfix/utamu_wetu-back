import graphene
import graphql_jwt
# Import your custom mutation from the users app schema
from apps.users.schema import CustomObtainJSONWebToken 
import apps.store.schema
import apps.users.schema
import apps.orders.schema

class Query(
    apps.store.schema.Query, 
    apps.users.schema.Query, 
    apps.orders.schema.Query, 
    graphene.ObjectType
):
    pass

class Mutation(
    apps.users.schema.Mutation,
    apps.orders.schema.Mutation,
    apps.store.schema.Mutation,
    graphene.ObjectType
):
    # USE THE CUSTOM CLASS HERE
    token_auth = CustomObtainJSONWebToken.Field()
    
    # These remain standard from the library
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)