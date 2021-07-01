from django.urls import path

from ..views import Rooms, RoomSearchWord, RoomFilterParam, Review, Order, RoomDetailView

urlpatterns = [
    path('', Rooms.as_view()),
    path('/filter', RoomFilterParam.as_view()),
    path('/<int:room_id>', RoomDetailView.as_view()),
    path('/reviews', Review.as_view()),
    path('/order', Order.as_view()),
    path('/searchword', RoomSearchWord.as_view())
]
