import json
import jwt
import bcrypt

from django.test   import TestCase, Client
from unittest.mock import patch, MagicMock

from .models import User, SocialFlatform

class KaKaoSigninTest(TestCase):
    def setUp(self):
        user = User.objects.create(
            name     = "HAN",
            email    = "aaa@naver.com",
            password = "123123123",
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
            status_code = 200
            def json(self):
                return  {       
                    "id": 1781472800,
                    "connected_at": "2021-06-25T03:56:15Z",
                    "properties": {
                        "nickname": "BONG",
                        "profile_image": "http://k.kakaocdn.net/dn/O5Usl/btq6jiApAS1/oq9qr8UyYN3qFDJvaKjw9k/img_640x640.jpg",
                        "thumbnail_image": "http://k.kakaocdn.net/dn/O5Usl/btq6jiApAS1/oq9qr8UyYN3qFDJvaKjw9k/img_110x110.jpg"
                    },
                    "kakao_account": {
                        "profile_needs_agreement": False,
                        "profile": {
                            "nickname": "BONG",
                            "thumbnail_image_url": "http://k.kakaocdn.net/dn/O5Usl/btq6jiApAS1/oq9qr8UyYN3qFDJvaKjw9k/img_110x110.jpg",
                            "profile_image_url": "http://k.kakaocdn.net/dn/O5Usl/btq6jiApAS1/oq9qr8UyYN3qFDJvaKjw9k/img_640x640.jpg",
                            "is_default_image": False
                        },
                        "has_email": True,
                        "email_needs_agreement": False,
                        "is_email_valid": True,
                        "is_email_verified": True,
                        "email": "wearethe3@naver.com",
                        "has_phone_number": True,
                        "phone_number_needs_agreement": False,
                        "phone_number": "+82 10-3682-5643",
                        "has_birthday": True,
                        "birthday_needs_agreement": True,
                        "has_gender": True,
                        "gender_needs_agreement": False,
                        "gender": "male",
                        "is_kakaotalk_user": True
                }
            }

        client = Client()
        mocked_requests.get = MagicMock(return_value = MockedResponce())
        headers             = {'HTTP_AUTHORIZATION' : 'FAKE_ACCESS_TOKEN'}
        responce            = client.get("/users/login/kakao", **headers)

        access_token = responce.json()['access_token']

        self.assertEqual(responce.json(), {"access_token" : access_token})
        self.assertEqual(responce.status_code, 200)
