from django.urls import path

from ..views import UserWish

urlpatterns = [
    path('', UserWish.as_view())
]
