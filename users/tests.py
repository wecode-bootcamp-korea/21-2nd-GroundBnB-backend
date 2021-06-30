import json
import jwt
import bcrypt

from django.test   import TestCase, Client
from unittest.mock import patch, MagicMock

from groundbnb.settings.local import LOCAL_SECRET_KEY, ALGORITHM
from .models                  import User, SocialFlatform

class KaKaoSigninTest(TestCase):
    def setUp(self):
        user = User.objects.create(
            name     = "HAN",
            email    = "aaa@naver.com",
            
        )
        SocialFlatform.objects.create(
            provider_name = 'kakao',
            provider_id   = '101010',
            profile_image = 'http://hahahahaha.jpg',
            nick_name     = 'HAN',
            user          = user
        )
        

    def tearDown(self):
        User.objects.all().delete()
        SocialFlatform.objects.all().delete()

    @patch("users.views.requests")
    def test_kakao_signin_new_user_success(self, mocked_requests):
        class MockedResponce:
            def json(self):
                return  {
                        "id"            : 12345,
                        "properties"    : {"nickname" : "test_user"},
                        "kakao_account" : {"email"    : "test@gmail.com"}
                    }
        client = Client()
        mocked_requests.get = MagicMock(return_value = MockedResponce())
        headers             = {'Authoriazation' : 'FAKE_ACCESS_TOKEN'}
        responce            = client.get("/users/login/kakao", content_type = 'application/json', **headers)

        access_token   = jwt.encode({'user_id': 12345}, LOCAL_SECRET_KEY, algorithm=ALGORITHM)

        self.assertEqual(responce.status_code, 200)
        self.assertEqual(responce.json(), 
            {
                'message'      : 'SUCCESS',
                'access_token' : f'{access_token}',
            }
        )
        