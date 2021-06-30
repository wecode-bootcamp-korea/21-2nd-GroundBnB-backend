import Json, jwt

from django.http            import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from .models             import User
from groundbnb.settings.local import LOCAL_SECRET_KEY, ALGORITHM

def UserTokenDeco(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token  = request.headers.get('Authorization', None)
            payload       = jwt.encode(access_token, LOCAL_SECRET_KEY, algorithm=ALGORITHM)
            request.user  = User.objects.get(email=payload['email'])

            return func(self, request, *args, **kwargs)

        except jwt.exceptions.DecodeError:
            return JsonResponse({'MESSAGE': 'INVALID_TOKEN'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_USER'}, status=400)
    
    return wrapper

def PublicUserDeco(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token  = request.headers.get('Authorization', None)

            if not access_token:
                request.user = 0
                return func(self, request, *args, **kwargs)    

            payload       = jwt.encode(access_token, LOCAL_SECRET_KEY, algorithm=ALGORITHM)
            request.user  = User.objects.get(email=payload['email'])

            return func(self, request, *args, **kwargs)

        except jwt.exceptions.DecodeError:
            return JsonResponse({'MESSAGE': 'INVALID_TOKEN'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'MESSAGE': 'INVALID_USER'}, status=400)
    
    return wrapper

    