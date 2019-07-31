from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ChessMatch, ChessPiece


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id', 'username', 'first_name',)

class ChessMatchSerializer(serializers.ModelSerializer):
  class Meta:
    model = ChessMatch
    fields = ('id', 'users',)

class ChessPieceSerializer(serializers.ModelSerializer):
  class Meta:
    model = ChessPiece
    fields = ('id', 'chess_match', 'piece_type', 'team',)
