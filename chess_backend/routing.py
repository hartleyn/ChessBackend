from .middleware import JWTAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from chess.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
  'websocket': JWTAuthMiddleware(
    URLRouter(
      websocket_urlpatterns
    )
  )
})
