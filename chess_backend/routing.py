from .middleware import TokenAuthMiddleware, JWTAuthMiddleware
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chess.routing

application = ProtocolTypeRouter({
  # Empty for now (http->django views is added by default)
  'websocket': JWTAuthMiddleware(
    URLRouter(
      chess.routing.websocket_urlpatterns
    )
  )
})
