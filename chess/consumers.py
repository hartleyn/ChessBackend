from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

from .move_validation import MoveValidator
from .models import ChessMatch, ChessPiece


class ChessMatchConsumer(WebsocketConsumer):
  #groups = ["broadcast"]

  @staticmethod
  def move_piece(pk, piece_pk, row, column, format=None):
    match = ChessMatch.objects.get(pk=pk)
    pieces = ChessPiece.objects.filter(chess_match=match)
    piece = pieces.get(pk=piece_pk)

    validator = MoveValidator(pieces, piece, row, column)
    move_valid = validator.move_is_valid()
    if move_valid:
      piece.row = row
      piece.column = column
      piece.move_count += 1
      piece.save()
    return {
      'id': piece.id, 
      'team': piece.get_team_display(), 
      'piece_type': piece.get_piece_type_display(), 
      'row': piece.row, 
      'column': piece.column, 
      'move_count': piece.move_count,
      'move_valid': move_valid,
    }

  def user_has_match_access(self):
    match = ChessMatch.objects.get(pk=self.match_id)
    users = match.users.values()
    for user in users:
      if self.user['user_id'] == user['id']:  # Changed user['id'] to user['user_id'] for use with JWT middleware
        return True
    return False

  def connect(self):
    # Called on connection.
    self.match_id = self.scope['url_route']['kwargs']['match_id']
    if self.scope['user']:
      self.user = self.scope['user']
    else:
      self.close()
    self.room_group_name = f'match_{self.match_id}'

    # Check that user has access to match
    if self.user_has_match_access():
      # Join room group
      async_to_sync(self.channel_layer.group_add)(
        self.room_group_name,
        self.channel_name
      )

      # To accept the connection call:
      self.accept()
      self.send(text_data=json.dumps({
        'message': f'Hello {self.user}!'
      }))
    else:
      self.close()
    

  def receive(self, text_data=None, bytes_data=None):
    # Called with either text_data or bytes_data for each frame
    # You can call:
    #self.send(text_data="Message received!")
    text_data_json = json.loads(text_data)
    move_piece_message = text_data_json['message']
    print(move_piece_message)

    move_result = self.move_piece(self.match_id, move_piece_message['id'], move_piece_message['row'], move_piece_message['column'])

    # Send message to room group
    async_to_sync(self.channel_layer.group_send)(
      self.room_group_name,
      {
        'type': 'match_message',
        'message': move_result,
      }
    )
    '''
    self.send(text_data=json.dumps({
      'message': str(message)
    }))
    '''

  # Receive message from room group
  def match_message(self, event):
    message = event['message']

    # Send message to WebSocket
    self.send(text_data=json.dumps({
      'message': message
    }))

  def disconnect(self, close_code):
    # Called when the socket closes
    # Leave room group
    async_to_sync(self.channel_layer.group_discard)(
      self.room_group_name,
      self.channel_name
    )
