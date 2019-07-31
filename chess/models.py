from django.db import models
from django.contrib.auth.models import User


class ChessMatch(models.Model):
  users = models.ManyToManyField(User)

class ChessPiece(models.Model):
  chess_match = models.ForeignKey(
    ChessMatch,
    on_delete=models.CASCADE,
  )
  PAWN = 'P'
  ROOK = 'R'
  KNIGHT = 'KN'
  BISHOP = 'B'
  QUEEN = 'Q'
  KING = 'KI'
  PIECE_CHOICES = (
    (PAWN, 'Pawn'),
    (ROOK, 'Rook'),
    (KNIGHT, 'Knight'),
    (BISHOP, 'Bishop'),
    (QUEEN, 'Queen'),
    (KING, 'King'),
  )
  piece_type = models.CharField(
    max_length=2,
    choices=PIECE_CHOICES,
  )
  BLACK = 'B'
  WHITE = 'W'
  TEAM_CHOICES = (
    (BLACK, 'Black'),
    (WHITE, 'White'),
  )
  team = models.CharField(
    max_length=1,
    choices=TEAM_CHOICES,
  )
  row = models.PositiveSmallIntegerField()
  column = models.PositiveSmallIntegerField()
  move_count = models.PositiveSmallIntegerField(default=0)
  captured = models.BooleanField(default=False)
