from django.urls import path

from ..views      import Rooms, RoomFilterParam, RoomDetailView

urlpatterns = [
    path('', Rooms.as_view()),
    path('/filter', RoomFilterParam.as_view()),
    path('/<int:room_id>', RoomDetailView.as_view())
]
