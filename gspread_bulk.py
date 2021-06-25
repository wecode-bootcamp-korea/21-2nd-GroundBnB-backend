import gspread
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'groundbnb.settings.local')
django.setup()

from rooms.models import *
from users.models import *

gc = gspread.service_account(filename='key.json')
sh = gc.open('GROUNDBNB')

print(sh.worksheets())

for sheet in sh.worksheets():
    title = sheet.title
    print(title)
    for data in sheet.get_all_records():
        if title == 'users':
            User(
                id = data['id'],
                name = data['name'],
                birth = data['birth'],
                email = data['email'],
                password = data['password'],
                host = data['host'],
                is_deleted = data['is_deleted']
            ).save()
        if title == 'social_flatform':
            SocialFlatform(
                id = data['id'],
                provider_name = data['provider_name'],
                provider_id = data['provider_id'],
                profile_image = data['profile_image'],
                nick_name = data['nick_name'],
                user_id = data['user_id']
            ).save()
        if title == 'wishes':
            Wish(
                id = data['id'],
                user_id = data['user_id'],
                room_id = data['room_id']
            ).save()
        if title == 'rooms':
            Room(
                id = data['id'],
                name = data['name'],
                address = data['address'],
                price = data['price'],
                latitude = data['latitude'],
                longitude = data['longitude'],
                max_people = data['max_people'],
                description = data['description'],
                category_id = data['category_id'],
                room_type_id = data['room_type_id'],
                guest_type = data['guest_type']
            ).save()
        if title == 'images':
            Image(
                id = data['id'],
                storage_path = data['storage_path'],
                file_name = data['file_name'],
                room_id = data['room_id']
            ).save()
        if title == 'room_reservations':
            RoomReservation(
                id = data['id'],
                check_in_date = data['check_in_date'],
                check_out_date = data['check_out_date'],
                adult = data['adult'],
                kids = data['kids'],
                baby = data['baby'],
                user_id = data['user_id'],
                room_id = data['room_id']
            ).save()
        if title == 'room_types':
            RoomType(
                id = data['id'],
                name = data['name']
            ).save()
        if title == 'room_option_infos':
            RoomOptionInfo(
                id = data['id'],
                room_id = data['room_id'],
                room_option_id = data['room_option_id'],
                quantity = data['quantity'],
            ).save()
        if title == 'room_options':
            RoomOption(
                id = data['id'],
                name = data['name']
            ).save()
        if title == 'room_reviews':
            RoomReview(
                id = data['id'],
                user_id = data['user_id'],
                room_id = data['room_id'],
                content = data['content'],
                depth = data['depth'],
                group = data['group'],
                is_deleted = data['is_deleted']
            ).save()
        if title == 'review_evaluations':
            ReviewEvaluation(
                id = data['id'],
                review_id = data['review_id'],
                evaluation_id = data['evaluation_id'],
                point = data['point']
            ).save()
        if title == 'evaluations':
            Evaluation(
                id = data['id'],
                name = data['name']
            ).save()
        if title == 'conveniences':
            Convenience(
                id = data['id'],
                name = data['name']
            ).save()
        if title == 'room_conveniences':
            RoomConvenience(
                id = data['id'],
                room_id = data['room_id'],
                convenience_id = data['convenience_id']
            ).save()
        if title == 'categories':
            Category(
                id = data['id'],
                name = data['name']
            ).save()