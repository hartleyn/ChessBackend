from django.contrib import admin
from .models import ChessMatch, ChessPiece

# Register your models here.
admin.site.register(ChessMatch)
admin.site.register(ChessPiece)
