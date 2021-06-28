from django.urls import path

from .views import KakaoLoginView, GoogleLoginView

urlpatterns = [
    # path('/signin/kakao', KaKaoSignInView.as_view()),
    # path('/signin/kakao/callback', KakaoSignInCallbackView.as_view()),
    path('/login/kakao', KakaoLoginView.as_view()),
    path('/login/google', GoogleLoginView.as_view()),   
]
