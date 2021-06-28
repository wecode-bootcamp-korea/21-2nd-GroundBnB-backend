import jwt

from django.http import JsonResponse

from .models                  import User
from groundbnb.settings.local import LOCAL_SECRET_KEY, ALGORITHM

def login_required(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token  = request.headers.get('Authorization', None)
            payload       = jwt.decode(access_token, LOCAL_SECRET_KEY, algorithm=ALGORITHM)
            request.user  = User.objects.get(email=payload['email'])

            return func(self, request, *args, **kwargs)

        except jwt.exceptions.DecodeError:
            return JsonResponse({'MESSAGE': 'INVALID_TOKEN'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_USER'}, status=400)
    
    return wrapper

def public_login_required(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token  = request.headers.get('Authorization', None)

            if not access_token:
                request.user = 0
                return func(self, request, *args, **kwargs)    

            payload       = jwt.decode(access_token, LOCAL_SECRET_KEY, algorithm=ALGORITHM)
            request.user  = User.objects.get(email=payload['email'])

            return func(self, request, *args, **kwargs)

        except jwt.exceptions.DecodeError:
            return JsonResponse({'MESSAGE': 'INVALID_TOKEN'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_USER'}, status=400)
    
    return wrapper