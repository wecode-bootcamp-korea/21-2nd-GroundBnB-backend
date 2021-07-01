from django.urls import path

from .views import KakaoLoginView, KakaoLogoutView, GoogleLoginView

urlpatterns = [
    path('/login/kakao', KakaoLoginView.as_view()),
    path('/logout/kakao', KakaoLogoutView.as_view()),
    path('/login/google', GoogleLoginView.as_view()),
    
]
