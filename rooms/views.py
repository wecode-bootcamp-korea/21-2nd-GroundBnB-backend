import sys, json

from django.http       import JsonResponse
from django.views      import View
from django.db.models  import Avg, Count, Q
from django.core.cache import cache

from functools import reduce

from .models import ReviewEvaluation, Room, RoomOption, Convenience, RoomType, RoomReview, Wish, Evaluation

# 소수 2째자리
FOMATTER = lambda x: 0 if not x else float(format(x, '.2f'))

class RoomFilterParam(View):
    # 프론트에서 벡엔드로 날려야 되는 파라미터
    def get(self, request):
        room_options     = cache.get_or_set('room_options', {option.id : option.name for option in RoomOption.objects.all()}, 60 * 60 * 24)
        room_convenience = cache.get_or_set('room_convenience', {option.id : option.name for option in Convenience.objects.all()},  60 * 60 * 24)
        
        result = {
            'room_type'        : [{'id' : type.id, 'name' : type.name} for type in RoomType.objects.all()],
            'room_convenience' : [{'id' : key, 'name' : value} for key,value in room_convenience.items()],
            'room_options'     : [{'id' : key, 'name' : value} for key,value in room_options.items()]
        }

        return JsonResponse({'result_filter_param' : result}, status=200)

class Rooms(View):
    def get(self, request):
        try:
            offset         = int(request.GET.get('offset', 1))
            limit          = int(request.GET.get('limit', 20))
            price_min      = request.GET.get('price_min', 0)
            price_max      = request.GET.get('price_max', sys.maxsize)
            max_people     = request.GET.get('max_people', None)     # 인원수
            room_type      = request.GET.get('room_type', None)      # 숙소유형
            bed            = request.GET.get('bed', None)            # 침대 Key
            bed_count      = request.GET.get('bed_count', None)      # 침대 개수
            bedroom        = request.GET.get('room', None)           # 침실 Key
            bedroom_count  = request.GET.get('bedroom_count', None)  # 침실 개수
            bathroom       = request.GET.get('bathroom', None)       # 욕실
            bathroom_count = request.GET.get('bathroom_count', None) # 욕실 개수
            convenience    = request.GET.get('convenience', None)    # 편의시설
            sw             = request.GET.get('sw', None)             # 남서쪽 좌표
            ne             = request.GET.get('ne', None)             # 북동쪽 좌표
            search         = request.GET.get('search', '')           # 검색어
            check_in       = request.GET.get('check_in', None)       # 체크인
            check_out      = request.GET.get('check_out', None)      # 체크아웃

            q = Q()

            # 좌표의 범위값을 구분하여 좌표 사이에 있는 모든방 검색
            if sw and ne:
                latitude_top    = ne.split(',')[0]
                latitude_bottom = sw.split(',')[0]
                longitude_left  = sw.split(',')[1]
                longitude_right = ne.split(',')[1]
                
                q &= Q(latitude__range = (latitude_top, latitude_bottom))
                q &= Q(latitude__range = (longitude_left, longitude_right))

            # 검색어가 주소일 경우
            if search:
                q &= Q(address__icontains = search)

            # 성인, 어린이, 유아의 총합계로 max_people를 계산
            if max_people:
                q &= Q(max_people__gte = max_people)

            # 예약가능일자 검색
            if check_in and check_out:
                q &= ~Q(Q(rooms_view__check_out_date__lt = check_out) & Q(rooms_view__check_in_date__gt = check_in))
                q |= Q(rooms_view__check_in_date__isnull = True)

            # 숙소유형
            if room_type:
                q &= Q(room_type_id__in = room_type)

            # 침대 & 침대 개수
            if bed and bed_count:
                q &= Q(roomoptioninfo__room_option_id = bed)
                q &= Q(roomoptioninfo__quantity = bed_count)

            # 침실 & 침실 개수
            if bedroom and bedroom_count:
                q &= Q(roomoptioninfo__room_option_id = bedroom)
                q &= Q(roomoptioninfo__quantity = bedroom_count)

            # 욕실 & 욕실 개수
            if bathroom and bathroom_count:
                q &= Q(roomoptioninfo__room_option_id = bathroom)
                q &= Q(roomoptioninfo__quantity = bathroom_count)

            # 편의시설
            if convenience:
                q &= Q(roomconvenience__convenience_id__in = convenience)

            # 요금     
            q &= Q(price__range = (price_min, price_max))

            room_options     = cache.get('room_options')
            room_convenience = cache.get('room_convenience')

            rooms = Room.objects.select_related('category', 'room_type') \
                                .filter(q) \
                                .prefetch_related(
                                    'rooms_view',
                                    'roomoptioninfo_set', 
                                    'image_set', 
                                    'wish_set', 
                                    'roomreview_set',
                                    'roomconvenience_set') \
                                .order_by('-id')[((offset - 1) * limit) : offset * limit]
                    
            result = {
                        'room_count' : len(rooms),
                        'next_page'  : offset + 1,
                        'search'     : search + '의 숙소' if search else '',
                        'rooms'      : [
                                            {
                                                'room_id'          : room.id,
                                                'category_id'      : room.category_id,
                                                'price'            : room.price,
                                                'address'          : room.address,
                                                'room_name'        : room.name,
                                                'room_images'      : [image.s3_url for image in room.image_set.all()],
                                                'max_people'       : room.max_people,
                                                'geo'              : {
                                                                        'latitude'  : room.latitude,
                                                                        'longitude' : room.longitude
                                                                     },
                                                'user_wish'        : 1 if room.wish_set.filter(user_id = 1, room_id = room).exists() else 0,
                                                'point_average'    : FOMATTER(ReviewEvaluation.objects.filter(
                                                                        review_id__in = room.roomreview_set.values('id')
                                                                    ).aggregate(Avg('point'))['point__avg']),
                                                'review_count'     : room.roomreview_set.count(),
                                                'room_options'     : [
                                                                        {
                                                                            'name'     : room_options[option.room_option_id],
                                                                            'quantity' : option.quantity
                                                                        } for option in room.roomoptioninfo_set.all()
                                                                    ],
                                                'room_convenience' : [room_convenience[convenience.convenience_id] for convenience in room.roomconvenience_set.all()]
                                            } for room in rooms
                                        ] 
                    }

            return JsonResponse({'rooms' : result}, status=200)
        except IndexError:
            return JsonResponse({'result' : 'INVALID GEOCODE'}, status=400)