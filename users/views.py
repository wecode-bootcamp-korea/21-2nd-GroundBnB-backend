import json, jwt, requests
from os import access

from django.views     import View
from django.http      import JsonResponse

from groundbnb.settings.local import LOCAL_SECRET_KEY, ALGORITHM
from users.models             import User, SocialFlatform

# client에서 받아온 카카오 서버 토큰으로 유저 검사
class KakaoLoginView(View):
    def get(self, request):
        try:
            kakao_token = request.headers.get('Authorization')
            api_url     = "https://kapi.kakao.com/v2/user/me"
            token_type  = "Bearer"

            if not kakao_token:
                return JsonResponse({'MESSAGE': "TOKEN REQUIRED"}, status=400)

            kakao_user_info = requests.get(api_url, headers= {'Authorization':f'{token_type} {kakao_token}'}).json()
            error_massage   = kakao_user_info.get('msg', None)
            
            if error_massage:
                return JsonResponse({'MESSAGE' : error_massage}, status=400)

            kakao_account = kakao_user_info.get("kakao_account", None)
            profile = kakao_account.get("profile", None)
            
            kakao_provider_id       = str(kakao_user_info.get('id')) 
            social_user             = SocialFlatform.objects.all()
            social_user_provider_id = []
            
            for i in social_user:
                social_user_provider_id.append(i.provider_id)

            if kakao_provider_id not in social_user_provider_id:
                user = User.objects.create(
                    name  = profile.get('nickname'),
                    email = kakao_account.get('email'),
                    birth = kakao_user_info.get('birth', None), # birth 정보 들어오면 데이터 타입 때문에 에러 확률 있음.
                )

                SocialFlatform.objects.create(
                    provider_name = 'kakao',
                    provider_id   = kakao_user_info.get('id'), 
                    profile_image = profile.get('profile_image_url'),
                    nick_name     = profile.get('nickname'),
                    user          = user
                )
                social_user_id = SocialFlatform.objects.get(user_id=user.id)           
                access_token   = jwt.encode({'id': social_user_id.id}, LOCAL_SECRET_KEY, algorithm=ALGORITHM)

                return JsonResponse({'MESSAGE': 'CREATED_USER', 'access_token': access_token}, status=200)
           
            user = SocialFlatform.objects.get(provider_id=kakao_provider_id)
            access_token   = jwt.encode({'id': user.id}, LOCAL_SECRET_KEY, algorithm=ALGORITHM)           

            return JsonResponse({'MESSAGE': 'EXISTS_USER', 'access_token': access_token}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

class GoogleLoginView(View):
    def get(self, request):
        try:
            access_token = request.headers.get('Authorization')
            url = 'https://www.googleapis.com/oauth2/v2/userinfo?access_token='

            response         = requests.get(url+access_token)
            google_user_info = response.json()

            if not access_token:
                return JsonResponse({'MESSAGE': 'TOKEN REQUIRED'}, status=400)
            
            # DB에 데이터 없을 때 신규회원으로 인식하고 회원가입
            google_user_info_email = google_user_info.get('email')
            google_provider_id     = google_user_info.get('id')

            ## 지정 scope 에 따라 응답 사용자 정보가 다름.
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
                access_token   = jwt.encode({'id': social_user_id.id}, LOCAL_SECRET_KEY, algorithm=ALGORITHM)

                return JsonResponse({'MESSAGE': 'CREATED_USER', 'access_token': access_token}, status=200)

            user = SocialFlatform.objects.get(provider_id=google_provider_id)
            access_token   = jwt.encode({'id': user.id}, LOCAL_SECRET_KEY, algorithm=ALGORITHM)           

            return JsonResponse({'MESSAGE': 'EXISTS_USER', 'access_token': access_token}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)