import json, jwt, requests

from django.views     import View
from django.http      import JsonResponse

from groundbnb.settings.local import LOCAL_SECRET_KEY, ALGORITHM
from users.models             import User, SocialFlatform

class KakaoAPI:
    def __init__(self, token):
        self.token = token
    
    def get_kakao_user(self):
        kakao_userinfo_url = "https://kapi.kakao.com/v2/user/me"
        headers            = {"Authorization" : f"Bearer {self.token}"}
        
        response = requests.get(kakao_userinfo_url, headers = headers, timeout=1000) 
        
        if response.status_code != 200:
            return JsonResponse({'MESSAGE' : 'RESPONSE_ERROR'}, status=400)

        return response.json()

    def request_kakao_logout(self):
        kakao_logout_url = 'https://kapi.kakao.com/v1/user/logout'
        headers          = {"Authorization" : f"Bearer {self.token}"}

        response = requests.get(kakao_logout_url, headers = headers)

        if response.status_code != 200:
            return JsonResponse({'MESSAGE' : 'RESPONSE_ERROR'}, status=400)
        
        return response.json()

class GoogleAPI:
    def __init__(self, token):
        self.token = token

    def get_google_user(self):
        google_userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo?access_token='
        response    = requests.get(f'{google_userinfo_url}{self.token}')

        if response.status_code != 200:
            return JsonResponse({'MESSAGE' : 'RESPONSE_ERROR'}, status=400)
            
        return response.json()

class KakaoLoginView(View):
    def get(self, request):
        try:
            access_token = request.headers.get('Authorization')

            if not access_token:
                return JsonResponse({'MESSAGE': 'TOKEN REQUIRED'}, status=400)

            kakao_user      = KakaoAPI(access_token)            
            kakao_user_info = kakao_user.get_kakao_user()
            kakao_account   = kakao_user_info.get('kakao_account')
            profile         = kakao_account.get('profile')
            
            user, created = User.objects.get_or_create(
                name  = profile.get('nickname'),
                birth = profile.get('birth', None),
                email = kakao_account.get('email')
            )
        
            if created:
                SocialFlatform.objects.create(
                    provider_name = 'kakao',
                    provider_id   = kakao_user_info.get('id'), 
                    profile_image = profile.get('profile_image_url'),
                    nick_name     = profile.get('nickname'),
                    user          = user
                )
                user.name  = profile.get('nickname')
                user.birth = profile.get('birth', None)
                user.email = kakao_account.get('email')
                user.save()
                
                social_user_id = SocialFlatform.objects.get(user_id=user.id)           
                access_token   = jwt.encode({'id': social_user_id.id, 'is_host' : user.host}, LOCAL_SECRET_KEY, algorithm=ALGORITHM)

                return JsonResponse({'MESSAGE': 'CREATED_USER', 'access_token': access_token}, status=200)

            kakao_id     = kakao_user_info.get('id')
            user         = SocialFlatform.objects.get(provider_id=kakao_id)
            is_host      = user.user.host
            access_token = jwt.encode({'id': user.id, 'is_host' : is_host}, LOCAL_SECRET_KEY, algorithm=ALGORITHM)           

            return JsonResponse({'MESSAGE': 'EXISTS_USER', 'access_token': access_token}, status=200)
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

class KakaoLogoutView(View):
    def post(self, request):
        access_token = request.headers.get('Authorization')
        kakao_user   = KakaoAPI(access_token)
        user_logout  = kakao_user.request_kakao_logout()
        
        return JsonResponse({'MESSAGE' : '로그아웃 되셨습니다아아.', 'token' : user_logout}, status=200)

class GoogleLoginView(View):
    def get(self, request):
        try:
            access_token = request.headers.get('Authorization')

            if not access_token:
                return JsonResponse({'MESSAGE': 'TOKEN REQUIRED'}, status=400)
            
            google_login_api       = GoogleAPI(access_token)
            google_user_info       = google_login_api.get_google_user()
            google_user_info_email = google_user_info.get('email')
            google_provider_id     = google_user_info.get('id')

            if not User.objects.filter(email=google_user_info_email).exists():
                user = User.objects.create(
                    name  = '',
                    email = google_user_info.get('email')
                )

                SocialFlatform.objects.create(
                    provider_name = 'google',
                    provider_id   = google_user_info.get('id'),
                    profile_image = google_user_info.get('picture'),
                    nick_name     = '',
                    user          = user
                )

                social_user_id = SocialFlatform.objects.get(user_id=user.id)           
                access_token   = jwt.encode({'id': social_user_id.id, 'is_host' : user.host}, LOCAL_SECRET_KEY, algorithm=ALGORITHM)

                return JsonResponse({'MESSAGE': 'CREATED_USER', 'access_token': access_token}, status=200)

            user         = SocialFlatform.objects.get(provider_id=google_provider_id)
            is_host      = user.user.host
            access_token = jwt.encode({'id': user.id, 'is_host': is_host}, LOCAL_SECRET_KEY, algorithm=ALGORITHM)           

            return JsonResponse({'MESSAGE': 'EXISTS_USER', 'access_token': access_token}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)
