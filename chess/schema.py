import graphene
from graphene_django.types import DjangoObjectType

from .models import ChessMatch, ChessPiece
from django.contrib.auth.models import User


class UserType(DjangoObjectType):
  class Meta:
    model = User

class ChessMatchType(DjangoObjectType):
  class Meta:
    model = ChessMatch

class ChessPieceType(DjangoObjectType):
  class Meta:
    model = ChessPiece

class Query(object):
  all_users = graphene.List(UserType)
  all_chess_matches = graphene.List(ChessMatchType)
  all_chess_pieces = graphene.List(ChessPieceType)

  def resolve_all_users(self, info, **kwargs):
    return User.objects.all()

  def resolve_all_chess_matches(self, info, **kwargs):
    return ChessMatch.objects.all()

  def resolve_all_chess_pieces(self, info, **kwargs):
    return ChessPiece.objects.all()
