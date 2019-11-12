import pytest
from .models import ChessPiece
from math import fabs
from unittest.mock import Mock


class MoveValidator:
  def __init__(self, all_pieces, piece, new_row, new_column):
    self.all_pieces = all_pieces
    self.piece = piece
    self.new_row = int(new_row)
    self.new_column = int(new_column)
    self.captured_piece_id = None

    self.forward_movement = -1 if self.piece.team == 'B' else 1
    self.en_passant_row = 3 if self.piece.team == 'B' else 4

  def _build_pawn_move_set(self):
    move_set = []
    range_limit = 1
    if self._pawn_can_double_jump():
      range_limit += 1
    move_set.extend(self._find_vertical_squares(range_limit=range_limit, direction_flag=self.forward_movement))
    move_set.extend(self._find_diagonal_squares(range_limit=1, x_direction_flag=1, y_direction_flag=self.forward_movement))
    move_set.extend(self._find_diagonal_squares(range_limit=1, x_direction_flag=-1, y_direction_flag=self.forward_movement))
    if self.piece.row == self.en_passant_row:
      move_set.extend(self._find_en_passant_squares())
    return move_set

  def _build_bishop_move_set(self):
    move_set = []
    move_set.extend(self._find_diagonal_squares(range_limit=8, x_direction_flag=1, y_direction_flag=1))
    move_set.extend(self._find_diagonal_squares(range_limit=8, x_direction_flag=-1, y_direction_flag=1))
    move_set.extend(self._find_diagonal_squares(range_limit=8, x_direction_flag=1, y_direction_flag=-1))
    move_set.extend(self._find_diagonal_squares(range_limit=8, x_direction_flag=-1, y_direction_flag=-1))
    return move_set
  
  def _find_en_passant_squares(self):
    available_squares = []
    en_passant_columns = [col for col in range(self.piece.column-1, self.piece.column+2, 2) if col <= 7 and col >= 0]
    en_passant_targets = [(self.piece.row, col) for col in en_passant_columns]
    for target_row, target_column in en_passant_targets:
      enemy_piece = self._piece_in_square(target_row, target_column, enemies_only=True)
      try:
        if enemy_piece.piece_type == 'P' and enemy_piece.move_count == 1:
          available_squares.append((target_row+(1 * self.forward_movement), target_column))
      except AttributeError:
        pass
    return available_squares

  def _find_vertical_squares(self, range_limit, direction_flag):
    available_squares = []
    for vertical_shift in range(1, range_limit + 1):
      new_row = self.piece.row + (vertical_shift * direction_flag)
      if self._coordinate_out_of_bounds(new_row):
        break
      piece_in_square = self._piece_in_square(new_row, self.piece.column)
      if not piece_in_square:
        available_squares.append((new_row, self.piece.column))
      elif piece_in_square.team != self.piece.team:
        if self.piece.piece_type != 'P':  # Pawns can only capture diagonally
          available_squares.append((new_row, self.piece.column))
        break
      elif piece_in_square.team == self.piece.team:
        break
    return available_squares

  def _find_horizontal_squares(self, range_limit, direction_flag):
    available_squares = []
    for horizontal_shift in range(1, range_limit + 1):
      new_column = self.piece.column + (horizontal_shift * direction_flag)
      if self._coordinate_out_of_bounds(new_column):
        break
      piece_in_square = self._piece_in_square(self.piece.row, new_column)
      if not piece_in_square:
        available_squares.append((self.piece.row, new_column))
      elif piece_in_square.team != self.piece.team:
        available_squares.append((self.piece.row, new_column))
        break
      elif piece_in_square.team == self.piece.team:
        break
    return available_squares

  def _find_diagonal_squares(self, range_limit, x_direction_flag, y_direction_flag):
    available_squares = []
    for diagonal_shift in range(1, range_limit + 1):
      new_row = self.piece.row + (diagonal_shift * y_direction_flag)
      if self._coordinate_out_of_bounds(new_row):
        break
      new_column = self.piece.column + (diagonal_shift * x_direction_flag)
      if self._coordinate_out_of_bounds(new_column):
        break
      piece_in_square = self._piece_in_square(new_row, new_column)
      if not piece_in_square:
        if self.piece.piece_type != 'P':  # Pawns can only move diagonally when capturing
          available_squares.append((new_row, new_column))
      elif piece_in_square.team != self.piece.team:
        available_squares.append((new_row, new_column))
        break
      elif piece_in_square.team == self.piece.team:
        break
    return available_squares

  def _piece_is_enemy(self, piece):
    return True if self.piece.team != piece.team else False

  def _pawn_can_double_jump(self):
    return True if self.piece.move_count == 0 else False 

  @staticmethod
  def _coordinate_out_of_bounds(coordinate):
    return True if coordinate > 7 or coordinate < 0 else False

  def move_is_valid(self):
    if self.piece.piece_type == 'P':
      move_set = self._build_pawn_move_set()
    elif self.piece.piece_type == 'B':
      move_set = self._build_bishop_move_set()
    
    else:
      return True

  def _piece_in_square(self, row, column, enemies_only=False):
    try:
      pieces = self.all_pieces
      if enemies_only:
        pieces = pieces.exclude(team=self.piece.team)
      piece = pieces.get(row=row, column=column)
      return piece
    except ChessPiece.DoesNotExist:
      return None


@pytest.mark.parametrize('team, row, column, range_limit, piece_in_square, expected_squares', [
  (
    'W', 1, 0, 6, None, [
    (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)
  ]),
  (
    'W', 1, 0, 2, None, [
    (2, 0), (3, 0)
  ]),
  (
    'W', 1, 0, 1, None, [
    (2, 0)
  ]),
  (
    'B', 6, 0, 6, None, [
    (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0)
  ]),
  (
    'B', 6, 0, 2, None, [
    (5, 0), (4, 0)
  ]),
  (
    'B', 6, 0, 1, None, [
    (5, 0)
  ]),
  # Boundary checking test cases
  (
    'W', 7, 0, 6, None, []
  ),
  (
    'W', 6, 0, 6, None, [
    (7, 0)
  ]),
  (
    'B', 0, 0, 6, None, []
  ),
  (
    'B', 1, 0, 6, None, [
    (0, 0)
  ]),
  # Blocked path test cases
  (
    'W', 1, 0, 6, Mock(team='B'), [
    (2, 0)
  ]),
  (
    'W', 1, 0, 6, Mock(team='W'), []
  ),
  (
    'B', 6, 0, 6, Mock(team='W'), [
    (5, 0)
  ]),
  (
    'B', 6, 0, 6, Mock(team='B'), []
  ),
])
def test__find_vertical_squares(team, row, column, range_limit, piece_in_square, expected_squares):
  all_pieces = Mock()
  piece = Mock(team=team, row=row, column=column)

  validator = MoveValidator(all_pieces, piece, -1, -1)
  validator._piece_in_square = Mock(return_value=piece_in_square)
  squares = validator._find_vertical_squares(range_limit, validator.forward_movement)  # Add boundary checking

  assert squares == expected_squares


@pytest.mark.parametrize('team, row, column, range_limit, direction_flag, piece_in_square, expected_squares', [
  # Right movement test cases
  (
    'W', 1, 0, 6, 1, None, [
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6)
  ]),
  (
    'W', 1, 0, 2, 1, None, [
    (1, 1), (1, 2)
  ]),
  (
    'W', 1, 0, 1, 1, None, [
    (1, 1)
  ]),
  (
    'B', 6, 0, 6, 1, None, [
    (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6)
  ]),
  (
    'B', 6, 0, 2, 1, None, [
    (6, 1), (6, 2)
  ]),
  (
    'B', 6, 0, 1, 1, None, [
    (6, 1)
  ]),
  # Left movement test cases
  (
    'W', 1, 7, 6, -1, None, [
    (1, 6), (1, 5), (1, 4), (1, 3), (1, 2), (1, 1)
  ]),
  (
    'W', 1, 7, 2, -1, None, [
    (1, 6), (1, 5)
  ]),
  (
    'W', 1, 7, 1, -1, None, [
    (1, 6)
  ]),
  (
    'B', 6, 7, 6, -1, None, [
    (6, 6), (6, 5), (6, 4), (6, 3), (6, 2), (6, 1)
  ]),
  (
    'B', 6, 7, 2, -1, None, [
    (6, 6), (6, 5)
  ]),
  (
    'B', 6, 7, 1, -1, None, [
    (6, 6)
  ]),
  # Boundary checking test cases
  (
    'W', 1, 7, 6, 1, None, []
  ),
  (
    'W', 1, 6, 6, 1, None, [
    (1, 7)
  ]),
  (
    'B', 6, 0, 6, -1, None, []
  ),
  (
    'B', 6, 1, 6, -1, None, [
    (6, 0)
  ]),
  # Blocked path test cases
  (
    'W', 1, 0, 6, 1, Mock(team='B'), [
    (1, 1)
  ]),
  (
    'W', 1, 0, 6, 1, Mock(team='W'), []
  ),
  (
    'B', 6, 7, 6, -1, Mock(team='W'), [
    (6, 6)
  ]),
  (
    'B', 6, 7, 6, -1, Mock(team='B'), []
  ),
])
def test__find_horizontal_squares(team, row, column, range_limit, direction_flag, piece_in_square, expected_squares):
  all_pieces = Mock()
  piece = Mock(team=team, row=row, column=column)

  validator = MoveValidator(all_pieces, piece, -1, -1)
  validator._piece_in_square = Mock(return_value=piece_in_square)
  squares = validator._find_horizontal_squares(range_limit, direction_flag)  # Add boundary checking

  assert squares == expected_squares


@pytest.mark.parametrize('team, row, column, range_limit, x_direction_flag, y_direction_flag, piece_in_square, expected_squares', [
  # Unlimited range, all directions test cases
  (
    'B', 3, 3, 8, 1, 1, None, [
    (4, 4), (5, 5), (6, 6), (7, 7)
  ]),
  (
    'B', 3, 3, 8, -1, 1, None, [
    (4, 2), (5, 1), (6, 0)
  ]),
  (
    'B', 3, 3, 8, 1, -1, None, [
    (2, 4), (1, 5), (0, 6)
  ]),
  (
    'B', 3, 3, 8, -1, -1, None, [
    (2, 2), (1, 1), (0, 0)
  ]),
  # Limited range, all directions test cases
  (
    'B', 3, 3, 2, 1, 1, None, [
    (4, 4), (5, 5)
  ]),
  (
    'B', 3, 3, 2, -1, 1, None, [
    (4, 2), (5, 1)
  ]),
  (
    'B', 3, 3, 2, 1, -1, None, [
    (2, 4), (1, 5)
  ]),
  (
    'B', 3, 3, 2, -1, -1, None, [
    (2, 2), (1, 1)
  ]),
  # Blocked path, all directions test cases
  (
    'B', 3, 3, 8, 1, 1, Mock(team='W'), [
    (4, 4)
  ]),
  (
    'B', 3, 3, 8, -1, 1, Mock(team='B'), []
  ),
  (
    'B', 3, 3, 8, 1, -1, Mock(team='W'), [
    (2, 4)
  ]),
  (
    'B', 3, 3, 8, -1, -1, Mock(team='B'), []
  ),
  (
    'B', 3, 3, 8, 1, 1, Mock(team='W'), [
    (4, 4)
  ]),
  (
    'B', 3, 3, 8, -1, 1, Mock(team='B'), []
  ),
  (
    'B', 3, 3, 8, 1, -1, Mock(team='W'), [
    (2, 4)
  ]),
  (
    'B', 3, 3, 8, -1, -1, Mock(team='B'), []
  ),
])
def test__find_diagonal_squares(team, row, column, range_limit, x_direction_flag, y_direction_flag, piece_in_square, expected_squares):
  all_pieces = Mock()
  piece = Mock(team=team, row=row, column=column)

  validator = MoveValidator(all_pieces, piece, -1, -1)
  validator._piece_in_square = Mock(return_value=piece_in_square)
  squares = validator._find_diagonal_squares(range_limit, x_direction_flag, y_direction_flag)  # Add boundary checking

  assert squares == expected_squares


@pytest.mark.parametrize('team, row, column, piece_in_square, expected_squares', [
  (
    'B', 3, 3, Mock(piece_type='P', move_count=1), [
    (2, 2), (2, 4)
  ]),
  (
    'B', 3, 3, Mock(piece_type='P', move_count=2), []
  ),
  (
    'B', 3, 3, Mock(piece_type='K', move_count=1), []
  ),
  (
    'B', 3, 3, None, []
  ),
  (
    'W', 4, 3, Mock(piece_type='P', move_count=1), [
    (5, 2), (5, 4)
  ]),
  (
    'W', 4, 3, Mock(piece_type='P', move_count=2), []
  ),
  (
    'W', 4, 3, Mock(piece_type='K', move_count=1), []
  ),
  (
    'W', 4, 3, None, []
  ),
  # Boundary checking test cases
  (
    'B', 3, 7, Mock(piece_type='P', move_count=1), [
    (2, 6)
  ]),
  (
    'W', 4, 0, Mock(piece_type='P', move_count=1), [
    (5, 1)
  ]),
])
def test__find_en_passant_squares(team, row, column, piece_in_square, expected_squares):
  all_pieces = Mock()
  piece = Mock(team=team, row=row, column=column)

  validator = MoveValidator(all_pieces, piece, -1, -1)
  validator._piece_in_square = Mock(return_value=piece_in_square)
  squares = validator._find_en_passant_squares()

  assert squares == expected_squares


@pytest.mark.parametrize('team, row, column, move_count, get_pieces_values, expected_squares', [
  (
    'W', 1, 3, 0, (
      None, None, Mock(team='B'), Mock(team='B')
    ), [
      (2, 2), (2, 3), (2, 4), (3, 3)
    ]
  ),
  (
    'W', 1, 3, 0, (
      Mock(team='B'), Mock(team='B'), Mock(team='B')
    ), [
      (2, 2), (2, 4)
    ]
  ),
  (
    'W', 1, 3, 0, (
      None, None, None, None
    ), [
      (2, 3), (3, 3)
    ]
  ),
  (
    'W', 1, 3, 0, (
      Mock(team='B'), None, None
    ), []
  ),
  (
    'B', 6, 3, 0, (
      None, None, Mock(team='W'), Mock(team='W')
    ), [
      (5, 2), (5, 3), (5, 4), (4, 3)
    ]
  ),
  (
    'B', 6, 3, 0, (
      Mock(team='W'), Mock(team='W'), Mock(team='W')
    ), [
      (5, 2), (5, 4)
    ]
  ),
  (
    'B', 6, 3, 0, (
      None, None, None, None
    ), [
      (5, 3), (4, 3)
    ]
  ),
  (
    'B', 6, 3, 0, (
      Mock(team='W'), None, None
    ), []
  ),
  # Boundary checking test cases
  (
    'W', 1, 0, 0, (
      Mock(team='B'), Mock(team='B'), Mock(team='B')
    ), [
      (2, 1)
    ]
  ),
  (
    'W', 7, 0, 0, (
      Mock(team='B'), Mock(team='B'), Mock(team='B')
    ), []
  ),
  (
    'B', 6, 7, 0, (
      Mock(team='W'), Mock(team='W'), Mock(team='W')
    ), [
      (5, 6)
    ]
  ),
  (
    'B', 0, 7, 0, (
      Mock(team='W'), Mock(team='W'), Mock(team='W')
    ), []
  ),
  # En passant test cases
  (
    'W', 4, 3, 1, (
      None, None, None, Mock(piece_type='P', move_count=1), Mock(piece_type='P', move_count=1)
    ), [
      (5, 2), (5, 3), (5, 4)
    ]
  ),
  (
    'W', 4, 3, 1, (
      None, None, None, Mock(piece_type='P', move_count=1), Mock(piece_type='P', move_count=2)
    ), [
      (5, 2), (5, 3)
    ]
  ),
  (
    'W', 4, 3, 1, (
      None, None, None, Mock(piece_type='P', move_count=1), Mock(piece_type='K', move_count=1)
    ), [
      (5, 2), (5, 3)
    ]
  ),
  (
    'B', 3, 3, 1, (
      None, None, None, Mock(piece_type='P', move_count=1), Mock(piece_type='P', move_count=1)
    ), [
      (2, 2), (2, 3), (2, 4)
    ]
  ),
  (
    'B', 3, 3, 1, (
      None, None, None, Mock(piece_type='P', move_count=1), Mock(piece_type='P', move_count=2)
    ), [
      (2, 2), (2, 3)
    ]
  ),
  (
    'B', 3, 3, 1, (
      None, None, None, Mock(piece_type='P', move_count=1), Mock(piece_type='K', move_count=1)
    ), [
      (2, 2), (2, 3)
    ]
  ),
])
def test__build_pawn_move_set(team, row, column, move_count, get_pieces_values, expected_squares):
  all_pieces = Mock()
  piece = Mock(team=team, row=row, column=column, piece_type='P', move_count=move_count)

  validator = MoveValidator(all_pieces, piece, -1, -1)
  validator._piece_in_square = Mock(side_effect=get_pieces_values)
  squares = validator._build_pawn_move_set()

  assert set(squares) == set(expected_squares)
  assert len(squares) == len(expected_squares)

@pytest.mark.parametrize('team, row, column, get_pieces_values, expected_squares', [
  (
    'B', 3, 3, (), [
      (4, 4), (5, 5), (6, 6), (7, 7), (4, 2), (5, 1), (6, 0), (2, 2), (1, 1), (0, 0), (2, 4), (1, 5), (0, 6)
    ]
  ),
])
def test__build_bishop_move_set(team, row, column, get_pieces_values, expected_squares):
  all_pieces = Mock()
  piece = Mock(team=team, row=row, column=column, piece_type='B')

  validator = MoveValidator(all_pieces, piece, -1, -1)
  #validator._piece_in_square = Mock(side_effect=get_pieces_values)
  validator._piece_in_square = Mock(return_value=None)
  squares = validator._build_bishop_move_set()

  assert set(squares) == set(expected_squares)
  assert len(squares) == len(expected_squares)
