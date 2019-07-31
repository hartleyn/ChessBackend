from django.urls import path, include
from . import views

from graphene_django.views import GraphQLView


urlpatterns = [
  path('matches/lobby/<int:pk>/', views.lobby),
  path('users/', views.UserList.as_view()),
  #path('users/register/', views.RegisterUser.as_view()),
  path('matches/', views.ChessMatchList.as_view()),
  path('matches/<int:pk>/', views.ChessMatchDetail.as_view()),
  path('matches/new/', views.CreateNewChessMatch.as_view()),
  path('matches/<int:pk>/join/', views.JoinChessMatch.as_view()),
  path('matches/<int:pk>/reset_pieces/', views.ResetMatch.as_view()),
  path('pieces/', views.ChessPieceList.as_view()),
  #path('matches/<int:pk>/move_piece/<int:piece_pk>/new_position/<int:row>/<int:column>/', views.MovePiece.as_view()),
  path('graphql/', GraphQLView.as_view(graphiql=True)),
]
