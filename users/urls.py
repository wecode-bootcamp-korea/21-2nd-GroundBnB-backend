from django.urls import path

from .views import KakaoLogoutView

urlpatterns = [
    path('/logout/kakao', KakaoLogoutView.as_view()),
]
