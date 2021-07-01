from django.urls import path

from .views import KakaoLoginView, GoogleLoginView

urlpatterns = [
    path('/login/kakao', KakaoLoginView.as_view()),
    path('/login/google', GoogleLoginView.as_view()),
]
