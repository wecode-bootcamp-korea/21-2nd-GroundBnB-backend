import json, requests

from django.views import View
from django.http  import JsonResponse

class KakaoAPI:
    def __init__(self, token):
        self.token = token
    
    def request_kakao_logout(self):
        kakao_logout_url = 'https://kapi.kakao.com/v1/user/logout'
        headers          = {"Authorization" : f"Bearer {self.token}"}

        response = requests.get(kakao_logout_url, headers = headers, timeout=1000)

        if response.status_code != 200:
            return JsonResponse({'MESSAGE' : 'RESPONSE_ERROR'}, status=400)
        
        return response.json()

class KakaoLogoutView(View):
    def post(self, request):
        access_token = request.headers.get('Authorization')
        kakao_user   = KakaoAPI(access_token)
        user_logout  = kakao_user.request_kakao_logout()
        
        return JsonResponse({'access_logout' : user_logout}, status=200)
