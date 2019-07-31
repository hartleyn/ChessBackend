import graphene
import chess.schema


class Query(chess.schema.Query, graphene.ObjectType):
  pass

schema = graphene.Schema(query=Query)
