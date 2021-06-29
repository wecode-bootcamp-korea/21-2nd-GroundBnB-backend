from django.urls import path
from ..views      import Rooms, RoomFilterParam

urlpatterns = [
    path('', Rooms.as_view()),
    path('/filter', RoomFilterParam.as_view()),
]