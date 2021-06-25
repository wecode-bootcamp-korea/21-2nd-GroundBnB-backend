from django.db import models

from users.models import User

class RoomOption(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = 'room_options'

class Category(models.Model):
    name = models.CharField(max_length=45)
    
    class Meta:
        db_table = 'categories'

class RoomType(models.Model):
    name = models.CharField(max_length=45)
    
    class Meta:
        db_table = 'room_types'

class Evaluation(models.Model):
    name = models.CharField(max_length=45)
    
    class Meta:
        db_table = 'evaluations'

class Convenience(models.Model):
    name = models.CharField(max_length=45)
    
    class Meta:
        db_table = 'conveniences'

class Room(models.Model):
    name             = models.CharField(max_length=45)
    address          = models.CharField(max_length=200)
    price            = models.DecimalField(max_digits=12, decimal_places=2)
    latitude         = models.CharField(max_length=45)
    longitude        = models.CharField(max_length=45)
    max_people       = models.IntegerField()
    description      = models.TextField()
    category         = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    room_type        = models.ForeignKey(RoomType, null=True, on_delete=models.SET_NULL)
    guest_type       = models.IntegerField()
    room_option_info = models.ManyToManyField(RoomOption, through='RoomOptionInfo')
    room_review      = models.ManyToManyField(User, through='RoomReview', related_name='room_review')
    room_reservation = models.ManyToManyField(User, through='RoomReservation', related_name='room_reservation')
    room_convenience = models.ManyToManyField(Convenience, through='RoomConvenience')
    user_wish        = models.ManyToManyField(User, through='Wish')

    class Meta:
        db_table = 'rooms'

class RoomOptionInfo(models.Model):
    room        = models.ForeignKey(Room, on_delete=models.CASCADE)
    room_option = models.ForeignKey(RoomOption, null=True, on_delete=models.SET_NULL)
    quantity    = models.IntegerField()

    class Meta:
        db_table = 'room_option_infos'

class RoomReview(models.Model):
    user              = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    room              = models.ForeignKey(Room, on_delete=models.CASCADE)
    content           = models.TextField()
    depth             = models.IntegerField()
    group             = models.IntegerField()
    created_at        = models.DateTimeField(auto_now_add=True)
    updata_at         = models.DateTimeField(auto_now=True)
    is_deleted        = models.BooleanField(default=False)
    review_evaluation = models.ManyToManyField(Evaluation, through='ReviewEvaluation')
    
    class Meta:
        db_table = 'room_reviews'

class RoomReservation(models.Model):
    check_in_date  = models.DateField()
    check_out_date = models.DateField()
    adult          = models.IntegerField(default=0)
    kids           = models.IntegerField(default=0)
    baby           = models.IntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    user           = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    room           = models.ForeignKey(Room, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'room_reservations'

class ReviewEvaluation(models.Model):
    review     = models.ForeignKey(RoomReview, on_delete=models.CASCADE)
    evaluation = models.ForeignKey(Evaluation, null=True, on_delete=models.SET_NULL)
    point      = models.FloatField()
    
    class Meta:
        db_table = 'review_evaluations'

class RoomConvenience(models.Model):
    room        = models.ForeignKey(Room, on_delete=models.CASCADE)
    convenience = models.ForeignKey(Convenience, null=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table = 'room_conveniences'

class Image(models.Model):
    storage_path = models.CharField(max_length=2000)
    file_name    = models.CharField(max_length=200)
    room         = models.ForeignKey(Room, on_delete=models.CASCADE)

    class Meta:
        db_table = 'images'

class Wish(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    class Meta:
        db_table = 'wishes'