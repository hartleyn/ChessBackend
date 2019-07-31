from .models import ChessPiece
from math import fabs


class MoveValidator:
  def __init__(self, all_pieces, piece, new_row, new_column):
    self.all_pieces = all_pieces
    self.piece = piece
    self.new_row = int(new_row)
    self.new_column = int(new_column)
    self.captured_piece_id = None

    if self.piece.team == 'B':
      self.forward_movement = -1
    else:
      self.forward_movement = 1

  def move_is_valid(self):
    if self.piece.piece_type == 'P':
      # STANDARD 1 SQUARE MOVE
      print(f'row: {self.piece.row}, new_row: {self.new_row}', self.new_row == self.piece.row + (1 * self.forward_movement))
      if self.new_row == self.piece.row + (1 * self.forward_movement) and self.new_column == self.piece.column and self.square_is_vacant():
        return True
      # DOUBLE JUMP MOVE, MUST BE FIRST MOVE
      elif self.new_row == self.piece.row + (2 * self.forward_movement) and self.new_column == self.piece.column and self.square_is_vacant() and self.piece.move_count == 0:
        return True
      # STANDARD DIAGONAL CAPTURE
      elif self.new_row == self.piece.row + (1 * self.forward_movement) and int(fabs(self.new_column - self.piece.column)) == 1 and self.square_is_enemy_occupied():
        return True
      # EN PASSANT CAPTURE, ENEMY MUST BE DOUBLE JUMPED PAWN
      elif self.new_row == self.piece.row + (1 * self.forward_movement) and int(fabs(self.new_column - self.piece.column)) == 1 and self.can_en_passant():
        return True
      else:
        return False
    else:
      return True


  def square_is_vacant(self):
    try:
      self.all_pieces.get(row=self.new_row, column=self.new_column)
      return False
    except ChessPiece.DoesNotExist:
      return True

  def square_is_enemy_occupied(self):
    try:
      enemy_piece = self.all_pieces.exclude(team=self.piece.team).get(row=self.new_row, column=self.new_column)
      self.captured_piece_id = enemy_piece.id
      return True
    except ChessPiece.DoesNotExist:
      pass

    for piece in self.all_pieces.filter(team=self.piece.team):
      if piece.row == self.new_row and piece.column == self.new_column:
        return True
    return False

  def can_en_passant(self):
    if self.piece.team == 'B':
      double_jump_row = 3
    else:
      double_jump_row = 4
    try:
      double_jumped_pawn = self.all_pieces.exclude(team=self.piece.team).get(piece_type='P', row=double_jump_row, column=self.new_column, move_count=1)
      self.captured_piece_id = double_jumped_pawn.id
      return True
    except ChessPiece.DoesNotExist:
      return False


'''
class MoveValidator:
  def __init__(self, all_pieces, piece, new_row, new_column):
    self.all_pieces = all_pieces
    self.piece = piece
    self.new_row = new_row
    self.new_column = new_column

  def square_is_occupied(self):
    occupied = False
    for piece in self.all_pieces:
      if piece.row == self.new_row and piece.column == self.new_column and piece.team == self.piece.team:
        occupied = True
        return occupied
    return occupied

  def square_is_inbounds(self):
    inbouds = False
    if self.new_row >= 0 and self.new_row < 8 and self.new_column >= 0 and self.new_column < 8:
      inbouds = True
    return inbouds

  def pawn_can_double_jump(self):
    can_double_jump = False
    if self.piece.piece_type == 'P' and self.piece.move_count == 0:
      can_double_jump = True
    return can_double_jump

  def king_can_castle(self):
    can_castle = False
    if self.piece.piece_type == 'K' and self.piece.move_count == 0:
      can_castle = True
    return can_castle

  def find_castling_rook(self):
    rooks = [piece for piece in self.all_pieces if piece.piece_type == 'R' and piece.team == self.piece.team]
    distances = []
    for rook in rooks:
      distance = int(fabs(rook.row - self.piece.new_row))
      distances.append(distance)
    min_distance = min(distances)
    closest_rook = rooks[distances.index(min_distance)]
    return closest_rook

  def rook_can_castle(self):
    rook = self.find_castling_rook()
    can_castle = False
    if rook.move_count == 0:
      can_castle = True
    return can_castle
'''
