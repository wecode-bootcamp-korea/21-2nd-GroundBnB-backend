from django.urls import path, include

from .views import Rooms

urlpatterns = [
    path('', Rooms.as_view())
]
