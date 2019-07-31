import jwt
from .settings import SECRET_KEY
from django.db import close_old_connections

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class JWTAuthMiddleware:
  """
  Custom middleware that finds the user by decoding the JWT (JSON Web Token) in the query string.
  The user is then added to the URLRouter scope.
  """
  def __init__(self, inner):
    self.inner = inner

  def __call__(self, scope):
    try:
      jwt_token = scope['query_string'].decode('utf-8')
      user = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
    except jwt.exceptions.ExpiredSignatureError:
      user = None
    except jwt.exceptions.InvalidSignatureError:
      user = None

    # Return the inner application directly and let it run everything else
    return self.inner(dict(scope, user=user))

class TokenAuthMiddleware:
  """
  Custom middleware that finds user by the token in the query string.
  """
  def __init__(self, inner):
    self.inner = inner

  def __call__(self, scope):
    # Close old database connections to prevent usage of timed out connections
    close_old_connections()
    #print(scope)
    #print(type(scope['query_string']))
    try:
      token = Token.objects.get(pk=scope['query_string'].decode('utf-8'))
      user = User.objects.get(pk=token.user.id)
    except Token.DoesNotExist:
      user = None

    # Return the inner application directly and let it run everything else
    return self.inner(dict(scope, user=user))
