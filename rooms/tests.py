import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'groundbnb.settings.test')
django.setup()

from django.test       import TestCase, Client
from django.core.cache import cache

from rooms.models import Room, RoomType, RoomOption, Convenience, Category, RoomOptionInfo, Image
from users.models import User

client = Client()

class RoomTest(TestCase):
    def setUp(self):
        ### test_roomfilterparam_get_view 테스트 데이터 생성 ###
        for i in range(1, 7):
            RoomType.objects.create(
                name = f'test{i}'
            )
            
        for i in range(1, 4):
            RoomOption.objects.create(
                name = f'test{i}'
            )

        for i in range(1, 11):
            Convenience.objects.create(
                name = f'test{i}'
            )
            
        ### test_rooms_get_view 테스트 데이터 생성 ###
        cache.get_or_set('room_count', Room.objects.count())
        cache.get_or_set('room_options', {option.id : option.name for option in RoomOption.objects.all()})
        cache.get_or_set('room_convenience', {option.id : option.name for option in Convenience.objects.all()})
        
        User.objects.create(
            name = 'unit_test_user',
            email = 'unit@test.com',
            birth = '9999-12-31',
            password = '1234',
            host = 0
        )
        
        Category.objects.create(name = 'test_category')
        
        Room.objects.create(
            name = 'unit_test_room',
            address = 'test시 test구 test동 119-112',
            price = 10000000,
            latitude = '32.63559209814935',
            longitude = '131.36942646064747',
            max_people = 9999,
            description = 'test입니다. test일껄?. test야',
            category_id = Category.objects.get(name = 'test_category').id,
            room_type_id = RoomType.objects.get(name = 'test1').id,
            guest_type = 1,
            host_id = User.objects.get(name = 'unit_test_user').id
        )
        
        Image.objects.create(
            storage_path = 'test/',
            file_name = 'test.png',
            room_id = Room.objects.get(name = 'unit_test_room').id
        )
        
        RoomOptionInfo.objects.create(
            room_id = Room.objects.get(name = 'unit_test_room').id,
            room_option_id = RoomOption.objects.get(name = 'test1').id,
            quantity = 1
        )

    def tearDown(self):
        RoomOptionInfo.objects.filter(
            room_id = Room.objects.get(name = 'unit_test_room').id,
            room_option_id = RoomOption.objects.get(name='test1').id
        ).delete()

        Image.objects.filter(
            storage_path = 'test/',
            file_name = 'test.png',
            room_id = Room.objects.get(name = 'unit_test_room').id        
        ).delete()

        Room.objects.filter(name = 'unit_test_room').delete()

        Category.objects.filter(name = 'test_category').delete()

        User.objects.filter(name = 'unit_test_user').delete()

        RoomType.objects.filter(name__icontains = 'test').delete()
        RoomOption.objects.filter(name__icontains = 'test').delete()
        Convenience.objects.filter(name__icontains = 'test').delete()

        cache.delete('room_count')
        cache.delete('room_options')
        cache.delete('room_convenience')

    def test_roomfilterparam_get_view(self):
        ### 200 TEST ###
        response = client.get('/rooms/filter')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json(), {
            "result_filter_param": {
                "room_type": [
                    {
                        'id' : roomtype.id,
                        'name' : roomtype.name
                    } for roomtype in RoomType.objects.all()
                ],
                "room_options": [
                    {
                        'id' : roomoption.id,
                        'name' : roomoption.name
                    } for roomoption in RoomOption.objects.all()
                ],
                "room_convenience": [
                    {
                        'id' : convenience.id,
                        'name' : convenience.name
                    } for convenience in Convenience.objects.all()
                ]}
            })
            
    def test_rooms_get_view(self):
        ### TEST PARAM SETTING ###
        test_dic = {
            'offset'         : '1', 
            'limit'          : '20',
            'price_min'      : '10000000',     
            'price_max'      : '10000000',     
            'adult'          : '1',
            'room_type'      : RoomType.objects.get(name = 'test1').id,  
            'bed'            : RoomOption.objects.get(name ='test1').id,     
            'bed_count'      : '1',
            'sw'             : '32,131',    
            'ne'             : '33,132',    
            'search'         : 'test',    
            'check_in'       : '2021-07-01',    
            'check_out'      : '2021-07-03'
        }

        room = Room.objects.filter(name = 'unit_test_room') \
                           .prefetch_related('roomoptioninfo_set', 'image_set') \
                           .first()

        ok_200_dic = {
            "rooms": {
                "room_count": cache.get('room_count'),
                "next_page": 2,
                "search": "test의 숙소",
                "adult": 1,
                "child": 0,
                "baby": 0,
                "rooms": [
                    {
                        "room_id": room.id,
                        "category_id": room.category.id,
                        "price": str(room.price),
                        "address": room.address,
                        "room_name": room.name,
                        "room_images": [room.image_set.all().first().s3_url],
                        "max_people": room.max_people,
                        "geo": {
                            "latitude": room.latitude,
                            "longitude": room.longitude
                        },
                        "user_wish": 0,
                        "point_average": 0,
                        "review_count": 0,
                        "room_options": [{'name':'test1', 'quantity':1}],
                        "room_convenience": []
                    }
                ]
            }
        }

        ### 200 TEST
        response = client.get('/rooms', test_dic)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),ok_200_dic)

        ### GEOCODE 400 SPLIT ERROR TEST
        test_dic['sw'] = '1,'
        response = client.get('/rooms', test_dic)
        self.assertEqual(response.status_code, 400)

        ### GEOCODE 400 INDEX ERROR TEST
        test_dic['sw'] = 0
        response = client.get('/rooms', test_dic)
        self.assertEqual(response.status_code, 400)

        ### QueryParameter VALUE ERROR TEST ##
        test_dic['sw'] = '32,131'
        test_dic['offset'] = 'test'
        response = client.get('/rooms', test_dic)
        self.assertEqual(response.status_code, 400)