from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
  url(r'^chess/matches/lobby/(?P<match_id>[0-9]+)/$', consumers.ChessMatchConsumer),
]
