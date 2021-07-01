import sys
import json
import decimal
import re

from django.http       import JsonResponse
from django.views      import View
from django.db.models  import Avg, Count, Q
from django.core.cache import cache

from functools import reduce

from .models      import ReviewEvaluation, Room, RoomOption, Convenience, RoomReservation, RoomType, RoomReview, Wish, Evaluation
from users.models import User
from users.utils  import public_login_required, login_required

# 소수 2째자리
FOMATTER = lambda x: 0 if not x else float(format(x, '.2f'))

class RoomSearchWord(View):
    # 메인페이지 연관검색어
    def get(self, request):
        search = str(request.GET.get('search', '')).replace(' ', '')

        if not search:
            return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400)
        
        address = Room.objects.raw('''
            SELECT row_number() over() as 
                id,
                room_address.address
              FROM (
                SELECT distinct substring_index(address, ' ', 3) as address 
                  FROM rooms
              ) room_address
            '''
        )

        result = []
        search_word = re.compile(f'{search}')
        address_dic = cache.get('address') or {}

        if not address_dic:
            for object in address:
                for i in range(0, len(object.address)):
                    word = object.address[0 : i + 1].replace(' ', '')

                    if address_dic.get(word.replace(' ', '')):
                        temp_list = address_dic[word]
                        
                        if not object.address in temp_list:
                            temp_list.append(object.address)
                            address_dic[word] = temp_list
                    else:
                        address_dic[word] = [object.address]
            
            cache.set('address', address_dic, 60 * 60 * 24)

        for key in address_dic.keys():
            if search_word.search(key):
                result.extend(address_dic[key])

        return JsonResponse({'result' : list(set(result))}, status=200)

class RoomFilterParam(View):
    # 프론트에서 벡엔드로 날려야 되는 파라미터
    def get(self, request):
        cache.get_or_set('room_count', Room.objects.count(), 60 * 60)
        room_options     = cache.get_or_set('room_options', {option.id : option.name for option in RoomOption.objects.all()}, 60 * 60 * 24)
        room_convenience = cache.get_or_set('room_convenience', {option.id : option.name for option in Convenience.objects.all()},  60 * 60 * 24)
        
        result = {
            'room_type'        : [{'id' : type.id, 'name' : type.name} for type in RoomType.objects.all()],
            'room_convenience' : [{'id' : key, 'name' : value} for key,value in room_convenience.items()],
            'room_options'     : [{'id' : key, 'name' : value} for key,value in room_options.items()]
        }

        return JsonResponse({'result_filter_param' : result}, status=200)

class Rooms(View):
    ### 숙소 리스트 ###
    def get(self, request):
        try:
            offset         = int(request.GET.get('offset', 1))
            limit          = int(request.GET.get('limit', 20))
            price_min      = int(request.GET.get('price_min', 0))
            price_max      = int(request.GET.get('price_max', sys.maxsize))
            adult          = int(request.GET.get('adult', 0))        # 어른수
            child          = int(request.GET.get('child', 0))        # 어린이수
            baby           = int(request.GET.get('baby', 0))         # 유아수
            max_people     = adult + child + baby                    # 인원수 합계
            room_type      = request.GET.get('room_type', None)      # 숙소유형
            bed            = request.GET.get('bed', None)            # 침대 Key, key : 1
            bed_count      = request.GET.get('bed_count', None)      # 침대 개수
            bedroom        = request.GET.get('bedroom', None)        # 침실 Key, key : 2
            bedroom_count  = request.GET.get('bedroom_count', None)  # 침실 개수
            bathroom       = request.GET.get('bathroom', None)       # 욕실 key, key : 3
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
                
                if not (latitude_top and latitude_bottom and longitude_left and longitude_right):
                    return JsonResponse({'result' : 'INVALID REQUEST'}, status=400)

                q &= Q(latitude__range = (latitude_bottom, latitude_top))
                q &= Q(longitude__range = (longitude_left, longitude_right))

            # 검색어가 주소일 경우
            if search:
                q &= Q(address__icontains = search)

            # 성인, 어린이, 유아의 총합계로 max_people를 계산
            if max_people:
                q &= Q(max_people__gte = max_people)

            # 예약가능일자 검색
            if check_in and check_out:
                q &= (
                        ~Q(Q(rooms_view__check_out_date__lt = check_out) & Q(rooms_view__check_in_date__gt = check_in))
                         | Q(rooms_view__check_in_date__isnull = True)
                     )

            # 숙소유형
            if room_type:
                q &= Q(room_type_id__in = room_type.split(','))

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
                q &= Q(roomconvenience__convenience_id__in = convenience.split(','))

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
                        'room_count' : cache.get('room_count') if len(rooms) else 0,
                        'next_page'  : offset + 1 if len(rooms) else 1,
                        'search'     : search + '의 숙소' if search else '',
                        'adult'      : adult,
                        'child'      : child,
                        'baby'       : baby,
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
                                                                        'lat' : decimal.Decimal(room.latitude),
                                                                        'lng' : decimal.Decimal(room.longitude)
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
            return JsonResponse({'MESSAGE' : 'INVALID GEOCODE'}, status=400)
        except ValueError:
            return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400)

class RoomDetailView(View):
    @public_login_required
    def get(self, request, room_id):
        try:
            room               = Room.objects.select_related('host').prefetch_related('image_set', 'host__socialflatform_set', 'roomoptioninfo_set', 'roomconvenience_set', 'roomreview_set').get(id=room_id)
            is_wish            = True if Wish.objects.filter(user_id = request.user, room_id = room).exists() else False
            image_urls         = [image.s3_url for image in room.image_set.all()]
            host_profile_image = room.host.socialflatform_set.all()[0].profile_image
            room_options       = [{
                'name':option.room_option.name, 
                'quantity':option.quantity
            } for option in room.roomoptioninfo_set.all()]
            room_conveniences  = [
                {
                    'name':convenience.convenience.name, 
                    'exist':(
                        True if convenience.convenience_id == convenience.id else False
                            )
                } for convenience in room.roomconvenience_set.all()
            ]
            reviews = [
                {
                    'name'          :review.user.name, 
                    'profile_image' :review.user.socialflatform_set.all()[0].profile_image 
                        if review.user.socialflatform_set.exists() else None, 
                    'created_at'    :review.created_at.date(),
                    'content'       :review.content, 
                    'review_id'     :review.id
                } for review in room.roomreview_set.all().order_by('-created_at')[:7]
            ]
            evaluations = Evaluation.objects\
                .filter(reviewevaluation__review__room_id=room.id)\
                .annotate(point_avg=Avg('reviewevaluation__point'))
            points = [
                {
                    'name':evaluation.name, 
                    'points':FOMATTER(evaluation.point_avg)
                } for evaluation in evaluations
            ]
            point_average = FOMATTER(ReviewEvaluation.objects.all().aggregate(Avg('point'))['point__avg'])
                    
            result = [
                {
                    'room_id'            : room.id,
                    'category_id'        : room.category_id,
                    'title'              : room.name,
                    'address'            : room.address,
                    'user_wish'          : is_wish,
                    'images'             : image_urls,
                    'price'              : room.price,
                    'max_people'         : room.max_people,
                    'host_name'          : room.host.name, 
                    'host_profile_image' : host_profile_image,
                    'room_options'       : room_options,
                    'description'        : room.description,
                    'room_convenience'   : room_conveniences,
                    'reviews'            : reviews,
                    'points'             : points,
                    'point_average'      : point_average,
                    'review_count'       : room.room_review.count(),
                    'lat'                : float(room.latitude),
                    'lng'                : float(room.longitude)
                }
            ]

            return JsonResponse({'message': 'SUCCESS', 'result': result}, status=200)
        
        except Room.DoesNotExist:
            return JsonResponse({'message': 'DOSE_NOT_EXIST_VALUE'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'},status=400)

class Review(View):
    ### 리뷰 보기 ###
    @public_login_required
    def get(self, request):
        try:
            # 로그인 하지 않은 유저는 0값으로 들어옮
            user_id    = request.user
            search     = request.GET.get('search', None)
            room_id    = request.GET.get('room_id', None)
            offset     = int(request.GET.get('offset', 1))
            limit      = int(request.GET.get('limit', 10))
            user_infos = None
            user_info  = {}

            if not room_id:
                return JsonResponse({'result':'INVALID REQUEST'}, status=400)

            q = Q()

            if search:
                q &= Q(content__icontains = search)
            
            q &= Q(room_id = room_id)
            
            evaluations = Evaluation.objects.all()
            reviews     = RoomReview.objects.select_related('room') \
                                            .filter(q) \
                                            .prefetch_related('user__socialflatform_set') \
                                            .order_by('-group_id', 'depth', 'id')[((offset - 1) * limit) : offset * limit]
                                            
            # 로그인한 유저가 상세페이지 댓글 모달을 눌렀을때의 경우
            if user_id:
                user_infos = User.objects.prefetch_related('roomreview_set', 'roomreservation_set') \
                                         .filter(id = user_id) \
                                         .first()

                # 해당 유저가 현재 room에 결제를 한적이 있는지 체크
                pay_count = user_infos.roomreservation_set.filter(room_id = room_id).aggregate(Count('id'))['id__count']

                # 해당 유저가 현재 room에 리뷰를 남긴적이 있는지 체크
                review_count = user_infos.roomreview_set.filter(room_id = room_id).aggregate(Count('id'))['id__count']
                
                # User 정보가 host일 경우, 현재 자기가 호스팅하고 RoomReview의 권한을 판단해야함
                host_auth = 0
                if user_infos.host and (reviews.first().room.host_id if len(reviews) else 0) == user_infos.id: 
                    host_auth = 1

                user_info['user_id']    = user_infos.id
                user_info['user_name']  = user_infos.name
                user_info['host_auth']  = host_auth
                user_info['reply_auth'] = 1 if pay_count > review_count else 0

            result = {
                'room_id'       : room_id,
                'next_page'     : offset + 1 if len(reviews) else 1,
                'reviews_count' : RoomReview.objects.all().aggregate(Count('id'))['id__count'],
                'point'   : [
                    {
                        'id'    : evaluation.id,
                        'name'  : evaluation.name,
                        'point' : FOMATTER(ReviewEvaluation.objects.filter(
                                    review_id__in=[review['id'] for review in reviews.values('id')],
                                    evaluation_id=evaluation.id
                                ).aggregate(Avg('point'))['point__avg'])
                    } for evaluation in evaluations
                ],
                'comment': [
                    {
                        'review_id'     : review.id,
                        'user_id'       : review.user.id,
                        'mine_comment'  : 1 if review.user.id == user_id else 0,
                        'user_name'     : review.user.name,
                        'profile_image' : review.user.socialflatform_set.filter(user_id=review.user_id).first().profile_image 
                                          if review.user.socialflatform_set.filter(user_id=review.user_id).exists() else '',
                        'content'       : review.content if not review.is_deleted else '삭제된 메세지 입니다.',
                        'depth'         : review.depth,
                        'group_id'      : review.group_id,
                        'created_at'    : review.created_at.strftime('%Y-%m-%d')
                    } for review in reviews
                ]
            }

            result['point_average']   = FOMATTER(reduce(lambda sum, dic: sum + dic['point'], result['point'], 0) / len(result['point'] or 0))
            result['login_user_info'] = user_info
            
            return JsonResponse({'reviews' : result}, status=200)
        except ValueError:
            return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400)

    ### review 작성 ###
    @login_required
    def post(self, request):
        try:
            user_id = request.user
            
            datas = json.loads(request.body)

            content  = datas['content']
            room_id  = int(datas['room_id'])
            group_id = int(datas['group_id']) if datas.get('group_id') else 0
               
            if not room_id:
                return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400)
            
            obj = RoomReview.objects.create(
                user_id  = user_id,
                room_id  = room_id,
                content  = content,
                depth    = 2 if group_id else 1,
                group_id = group_id
            )

            if not group_id:
                RoomReview.objects.filter(id = obj.id).update(group_id = obj.id)

            # 댓글을 남긴 후, 댓글 권한이 아직 남아 있는지 다시 체크
            # 2번 이상 결제 하고, 댓글을 한번도 안남겼을 경우도 있기 때문..
            user_infos = User.objects.prefetch_related('roomreview_set__room', 'roomreservation_set') \
                                     .filter(id = user_id, roomreview__room__id = room_id) \
                                     .first()

            # 해당 유저가 현재 room에 결제를 한적이 있는지 체크
            pay_count = user_infos.roomreservation_set.filter(room_id = room_id).aggregate(Count('id'))['id__count']

            # 해당 유저가 현재 room에 리뷰를 남긴적이 있는지 체크
            review_count = user_infos.roomreview_set.filter(room_id = room_id).aggregate(Count('id'))['id__count']

            # User 정보가 host일 경우, 현재 자기가 호스팅하고 RoomReview의 권한을 판단해야함
            host_auth = 0
            if user_infos.host and (user_infos.roomreview_set.all().first().room.host_id  == user_infos.id): 
                host_auth = 1

            return JsonResponse({'result' : {
                'review_id'    : obj.id,
                'group_id'     : obj.group_id if group_id else obj.id,
                'depth'        : obj.depth,
                'content'      : obj.content,
                'reply_auth'   : 1 if pay_count > review_count else 0,
                'host_auth'    : host_auth,
                'user_id'      : user_infos.id,
                'user_name'    : user_infos.name,
                'mine_comment' : 1
                }
            }, status=201)

        except KeyError:
            return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400)
        except ValueError:
            return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400)

    ### review 삭제 ###
    @login_required
    def delete(self, request):
        try:
            review_id = int(request.GET.get('review_id', 0))

            if not review_id:
                return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400)

            is_updated = RoomReview.objects.filter(id = review_id).update(is_deleted = 1)

            if not is_updated:
                return JsonResponse({'MESSAGE' : 'NOT EXISTS REVIEW'}, status=400)

            return JsonResponse({'MESSAGE' : 'SUCCESS'}, status=200)

        except ValueError:
            return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400)

    @login_required
    def patch(self, request):
        try:
            user_id   = request.user
            datas     = json.loads(request.body)
            review_id = int(datas['review_id'])
            content   = datas['content']

            is_updated = RoomReview.objects.filter(
                user_id = user_id,
                id      = review_id
            ).update(
                content = content
            )

            if not is_updated:
                return JsonResponse({'MESSAGE' : 'NOT EXISTS REVIEW'}, status=400) 

            return JsonResponse({'MESSAGE' : 'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400)
        except ValueError:
            return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE' : 'EMPTY BODY'}, status=400)

class UserWish(View):
    ### 위시리스트 ###
    @login_required
    def get(self, request):
        user_id = request.user

        wishes = Wish.objects.select_related('room') \
                             .filter(user_id = user_id) \
                             .prefetch_related('room__room_review', 'room__image_set')
                            
        result = [
            {
                'room_id'       : wish.room.id,
                'price'         : wish.room.price,
                'point_average' : FOMATTER(ReviewEvaluation.objects.filter(
                                    review_id__in = wish.room.roomreview_set.values('id')
                                ).aggregate(Avg('point'))['point__avg']),
                'user_wish'     : 1,
                'room_name'     : wish.room.name,
                'room_image'    : [image.s3_url for image in wish.room.image_set.all()],
                'review_count'  : wish.room.roomreview_set.all().aggregate(Count('id'))['id__count']
            } for wish in wishes
        ]

        return JsonResponse({'wishes' : result}, status=200)

    ### 위시 리스트 담기 ###
    @login_required
    def post(self, request):
        try:
            user_id = request.user
            data    = json.loads(request.body)
            room_id = data['room_id']

            if not room_id:
                return JsonResponse({'MESSAGE':'INVALID REQUEST'}, status=400)

            obj, created = Wish.objects.get_or_create(
                user_id = user_id,
                room_id = data['room_id']
            )

            if not created:
                return JsonResponse({'MESSAGE' : 'EXISTS WISH ROOM'}, status=400)
            
            return JsonResponse({'MESSAGE' : 'SUCCESS'}, status=201)

        except KeyError:
            return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE' : 'EMPTY BODY'}, status=400)

    ### 위시리스트 삭제 ###
    @login_required
    def delete(self, request):
        try:
            user_id = request.user
            room_id = int(request.GET.get('room_id', 0))

            is_deleted = Wish.objects.filter(user_id = user_id, room_id = room_id).delete()

            if not is_deleted[0]:
                return JsonResponse({'MESSAGE' : 'NOT EXISTS WISH ROOM'}, status=400)

            return JsonResponse({'MESSAGE' : 'SUCCESS'}, status=204)

        except ValueError:
            return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400)

class Order(View):
    ### 방예약 ###
    @login_required
    def post(self, request):
        try:
            user_id = request.user

            datas = json.loads(request.body)

            check_in_date  = datas['check_in_date']
            check_out_date = datas['check_out_date']
            adult          = datas['adult']
            kids           = datas['kids']
            baby           = datas['baby']
            room_id        = datas['room_id']

            if not(check_in_date and check_out_date and 
                    adult and kids and baby and room_id):
                return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400)

            room_reservation_info = RoomReservation.objects.filter(
                check_in_date  = datas['check_in_date'],
                check_out_date = datas['check_out_date'],
                room_id        = datas['room_id']
            )

            if room_reservation_info:
                return JsonResponse({'MESSAGE' : 'NOT EXISTS RESERVATION'}, status=200)

            RoomReservation.objects.create(
                check_in_date  = datas['check_in_date'],
                check_out_date = datas['check_out_date'],
                adult          = datas['adult'],
                kids           = datas['kids'],
                baby           = datas['baby'],
                user_id        = user_id,
                room_id        = datas['room_id']
            )

            return JsonResponse({'MESSAGE' : 'SUCCESS'}, status = 200)

        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE' : 'EMPTY BODY'}, status=400)

    ### 방예약 정보 수정 ###
    @login_required
    def patch(self, request):
        try:
            user_id = request.user

            datas = json.loads(request.body)

            room_id            = datas['room_id'],
            org_check_in_date  = datas['org_check_in_date']
            org_check_out_date = datas['org_check_out_date']
            check_in_date      = datas['check_in_date'],
            check_out_date     = datas['check_out_date']

            if not (room_id and org_check_in_date and org_check_out_date 
                        and check_in_date and check_out_date):
                return JsonResponse({'MESSAGE' : 'INVALID REQUEST'}, status=400) 

            is_updated = RoomReservation.objects.filter(
                user_id        = user_id,
                room_id        = room_id,
                check_in_date  = org_check_in_date,
                check_out_date = org_check_out_date
            ).update(
                check_in_date  = check_in_date,
                check_out_date = check_out_date
            )
            
            if not is_updated:
                return JsonResponse({'MESSAGE' : 'NOT EXISTS RESERVATION INFO'}, status=400)

            return JsonResponse({'MESSAGE' : 'SUCCESS'}, status=200)
            
        except KeyError:
            return JsonResponse({'MESSAGE' : 'INVALID ERROR'}, status=400)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE' : 'EMPTY BODY'}, status=400)
