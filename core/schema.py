import graphene
import apps.store.schema  

class Query(apps.store.schema.Query, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)