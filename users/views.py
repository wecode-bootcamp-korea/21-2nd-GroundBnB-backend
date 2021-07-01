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

class GoogleAPI:
    def __init__(self, token):
        self.token = token

    def get_google_user(self):
        google_userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo?access_token='
        response            = requests.get(f'{google_userinfo_url}{self.token}')

        if response.status_code != 200:
            return JsonResponse({'MESSAGE' : 'RESPONSE_ERROR'}, status=400)
            
        return response.json()

class KakaoLoginView(View):
    def get(self, request):
        try:
            access_token = request.headers.get('Authorization')

            if not access_token:
                return JsonResponse({'MESSAGE': 'TOKEN REQUIRED'}, status=400)

            kakao_api  = KakaoAPI(access_token)            
            kakao_user = kakao_api.get_kakao_user()
            
            user, created = User.objects.get_or_create(socialflatform__provider_id=kakao_user["id"])

            if created:
                user.name  = kakao_user["kakao_account"]["profile"]["nickname"]
                user.email = kakao_user["kakao_account"]["email"]
                user.save()
                
                SocialFlatform.objects.create(
                    provider_name = 'kakao',
                    provider_id   = kakao_user["id"], 
                    profile_image = kakao_user["kakao_account"]["profile"]["profile_image_url"],
                    nick_name     = kakao_user["kakao_account"]["profile"]["nickname"],
                    user          = user
                )
            
            access_token = jwt.encode({'id' : user.id, 'is_host' : user.host}, LOCAL_SECRET_KEY, algorithm=ALGORITHM)

            return JsonResponse({'access_token': access_token}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)            

class GoogleLoginView(View):
    def get(self, request):
        try:
            access_token = request.headers.get('Authorization')

            if not access_token:
                return JsonResponse({'MESSAGE': 'TOKEN REQUIRED'}, status=400)
            
            google_login_api = GoogleAPI(access_token)
            google_user_info = google_login_api.get_google_user()

            user, created = User.objects.get_or_create(socialflatform__provider_id=google_user_info["id"])

            if created:
                user.name  = ''
                user.email = google_user_info['email']
                user.save()

                SocialFlatform.objects.create(
                    provider_name = 'google',
                    provider_id   = google_user_info['id'],
                    profile_image = google_user_info['picture'],
                    nick_name     = '',
                    user          = user
                )

            access_token = jwt.encode({'id' : user.id, 'is_host' : user.host}, LOCAL_SECRET_KEY, algorithm=ALGORITHM)

            return JsonResponse({'access_token': access_token}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)
