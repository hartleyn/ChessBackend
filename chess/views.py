from django.shortcuts import render
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from .models import ChessMatch, ChessPiece
from .serializers import UserSerializer, ChessMatchSerializer, ChessPieceSerializer
from django.http import Http404
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions, authentication
from rest_framework.views import APIView
from rest_framework.response import Response

from .move_validation import MoveValidator


def lobby(request, pk):
  return render(request, 'matches/lobby.html', {})

class UserList(generics.ListAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer

  permission_classes = (permissions.IsAdminUser,)

'''
class RegisterUser(generics.CreateAPIView):
  """
  POST users/register/
  """
  def post(self, request, *args, **kwargs):
    username = request.data.get("username", "")
    password = request.data.get("password", "")
    confirm_password = request.data.get("confirm_password", "")
    email = request.data.get("email", "")
    if not username or not password or not email:
      return Response(
        data={
          "message": "username, password and email are required to register a user"
        },
        status=status.HTTP_400_BAD_REQUEST
      )
    elif password != confirm_password:
      return Response(
        data={
          "message": "passwords do not match"
        },
        status=status.HTTP_400_BAD_REQUEST
      )
    elif len(password) < 8:
      return Response(
        data={
          "message": "password must be at least 8 characters"
        },
        status=status.HTTP_400_BAD_REQUEST
      )
    
    try:
      new_user = User.objects.create_user(
        username=username, password=password, email=email
      )
    except IntegrityError:
      return Response(
        data={
          "message": "username already taken"
        },
        status=status.HTTP_400_BAD_REQUEST
      )

    return Response({"id": new_user.id, "username": new_user.username, "email": new_user.email}, status=status.HTTP_201_CREATED)

  permission_classes = (permissions.AllowAny,)
'''

class ChessMatchList(generics.ListAPIView):
  queryset = ChessMatch.objects.all()
  serializer_class = ChessMatchSerializer

  permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ResetMatch(APIView):
  @staticmethod
  def get_object(pk):
    try:
      return ChessMatch.objects.get(pk=pk)
    except ChessMatch.DoesNotExist:
      raise Http404

  @staticmethod
  def reset_pieces(pieces):
    black_pawns = pieces.filter(team='B', piece_type='P')
    white_pawns = pieces.filter(team='W', piece_type='P')
    
    for x in range(8):
      pawn = black_pawns[x]
      pawn.row = 6
      pawn.column = x
      pawn.save()

      pawn = white_pawns[x]
      pawn.row = 1
      pawn.column = x
      pawn.save()
      
    black_rooks = pieces.filter(team='B', piece_type='R')
    white_rooks = pieces.filter(team='W', piece_type='R')

    rook = black_rooks[0]
    rook.row = 7
    rook.column = 0
    rook.save()
    rook = black_rooks[1]
    rook.row = 7
    rook.column = 7
    rook.save()

    rook = white_rooks[0]
    rook.row = 0
    rook.column = 0
    rook.save()
    rook = white_rooks[1]
    rook.row = 0
    rook.column = 7
    rook.save()

    black_knights = pieces.filter(team='B', piece_type='KN')
    white_knights = pieces.filter(team='W', piece_type='KN')

    knight = black_knights[0]
    knight.row = 7
    knight.column = 1
    knight.save()
    knight = black_knights[1]
    knight.row = 7
    knight.column = 6
    knight.save()

    knight = white_knights[0]
    knight.row = 0
    knight.column = 1
    knight.save()
    knight = white_knights[1]
    knight.row = 0
    knight.column = 6
    knight.save()
    
    black_bishops = pieces.filter(team='B', piece_type='B')
    white_bishops = pieces.filter(team='W', piece_type='B')

    bishop = black_bishops[0]
    bishop.row = 7
    bishop.column = 2
    bishop.save()
    bishop = black_bishops[1]
    bishop.row = 7
    bishop.column = 5
    bishop.save()

    bishop = white_bishops[0]
    bishop.row = 0
    bishop.column = 2
    bishop.save()
    bishop = white_bishops[1]
    bishop.row = 0
    bishop.column = 5
    bishop.save()

    black_queen = pieces.get(team='B', piece_type='Q')
    white_queen = pieces.get(team='W', piece_type='Q')

    black_queen.row = 7
    black_queen.column = 4
    black_queen.save()

    white_queen.row = 0
    white_queen.column = 3
    white_queen.save()

    black_king = pieces.get(team='B', piece_type='K')
    white_king = pieces.get(team='W', piece_type='K')

    black_king.row = 7
    black_king.column = 3
    black_king.save()

    white_king.row = 0
    white_king.column = 4
    white_king.save()

    for piece in pieces:
      piece.captured = False
      piece.move_count = 0
      piece.save()

  def post(self, request, pk, format=None):
    match = self.get_object(pk)
    pieces = ChessPiece.objects.filter(chess_match=match)
    self.reset_pieces(pieces)
    return Response({'id': match.id, 'match_reset': True}, status=status.HTTP_205_RESET_CONTENT)

class CreateNewChessMatch(APIView):
  @staticmethod
  def create_pieces(match):
    for col in range(8):
      black_pawn = ChessPiece(chess_match=match, piece_type='P', team='B', row=6, column=col)
      black_pawn.save()
      white_pawn = ChessPiece(chess_match=match, piece_type='P', team='W', row=1, column=col)
      white_pawn.save()

    black_rook_1 = ChessPiece(chess_match=match, piece_type='R', team='B', row=7, column=0)
    black_rook_1.save()
    black_rook_2 = ChessPiece(chess_match=match, piece_type='R', team='B', row=7, column=7)
    black_rook_2.save()
    white_rook_1 = ChessPiece(chess_match=match, piece_type='R', team='W', row=0, column=0)
    white_rook_1.save()
    white_rook_2 = ChessPiece(chess_match=match, piece_type='R', team='W', row=0, column=7)
    white_rook_2.save()

    black_knight_1 = ChessPiece(chess_match=match, piece_type='KN', team='B', row=7, column=1)
    black_knight_1.save()
    black_knight_2 = ChessPiece(chess_match=match, piece_type='KN', team='B', row=7, column=6)
    black_knight_2.save()
    white_knight_1 = ChessPiece(chess_match=match, piece_type='KN', team='W', row=0, column=1)
    white_knight_1.save()
    white_knight_2 = ChessPiece(chess_match=match, piece_type='KN', team='W', row=0, column=6)
    white_knight_2.save()

    black_bishop_1 = ChessPiece(chess_match=match, piece_type='B', team='B', row=7, column=2)
    black_bishop_1.save()
    black_bishop_2 = ChessPiece(chess_match=match, piece_type='B', team='B', row=7, column=5)
    black_bishop_2.save()
    white_bishop_1 = ChessPiece(chess_match=match, piece_type='B', team='W', row=0, column=2)
    white_bishop_1.save()
    white_bishop_2 = ChessPiece(chess_match=match, piece_type='B', team='W', row=0, column=5)
    white_bishop_2.save()

    black_queen = ChessPiece(chess_match=match, piece_type='Q', team='B', row=7, column=4)
    black_queen.save()
    white_queen = ChessPiece(chess_match=match, piece_type='Q', team='W', row=0, column=3)
    white_queen.save()

    black_king = ChessPiece(chess_match=match, piece_type='K', team='B', row=7, column=3)
    black_king.save()
    white_king = ChessPiece(chess_match=match, piece_type='K', team='W', row=0, column=4)
    white_king.save()

  def post(self, request, format=None):
    request_data = request.data.copy()
    request_data.update({'users': [request.user.id]})
    serializer = ChessMatchSerializer(data=request_data)
    if serializer.is_valid():
      serializer.save()
      match = ChessMatch.objects.get(pk=serializer.data['id'])
      self.create_pieces(match)
      match.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class JoinChessMatch(APIView):
  """
  POST matches/<int:pk>/join/
  """
  @staticmethod
  def get_object(pk):
    try:
      return ChessMatch.objects.get(pk=pk)
    except ChessMatch.DoesNotExist:
      raise Http404
  
  def post(self, request, pk, format=None):
    match = self.get_object(pk)
    if len(match.users.values()) < 2:
      match.users.add(request.user)
      match.save()
      return Response({'id': match.id, 'joined_match': True}, status=status.HTTP_200_OK) # Add status codes
    return Response({'id': match.id, 'joined_match': False}, status=status.HTTP_400_BAD_REQUEST)

class ChessPieceList(generics.ListAPIView):
  queryset = ChessPiece.objects.all()
  serializer_class = ChessPieceSerializer

  permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class ChessMatchDetail(APIView):
  @staticmethod
  def get_object(pk):
    try:
      return ChessMatch.objects.get(pk=pk)
    except ChessMatch.DoesNotExist:
      raise Http404

  queryset = ChessMatch.objects.all()
  serializer_class = ChessMatchSerializer

  def get(self, request, pk, format=None):
    match = self.get_object(pk)
    users = []
    for user in match.users.all():
      users.append({'id': user.id, 'username': user.username})

    pieces = ChessPiece.objects.filter(chess_match=match).values()

    return Response({'id': match.id, 'users': users, 'pieces': pieces})

  permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

'''
class MovePiece(APIView):
  def post(self, request, pk, piece_pk, row, column, format=None):
    match = ChessMatch.objects.get(pk=pk)
    pieces = ChessPiece.objects.filter(chess_match=match)
    piece = pieces.get(pk=piece_pk)

    validator = MoveValidator(pieces, piece, row, column)
    #print(validator.square_is_occupied())

    if validator.square_is_occupied():
      return Response({'valid_move': False, 'reason': 'Square is occupied.'})
    elif not validator.square_is_inbounds():
      return Response({'valid_move': False, 'reason': 'Move is out of bounds.'})
    else:
      # IF VALID MOVE
      piece.row = row
      piece.column = column
      piece.move_count += 1
      piece.save()
      #print(piece.id)

      return Response({'valid_move': True, 'id': piece.id, 'chess_match_id': match.id, 'piece_type': piece.piece_type, 'team': piece.team, 'row': piece.row, 'column': piece.column, 'move_count': piece.move_count})

  permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
'''
