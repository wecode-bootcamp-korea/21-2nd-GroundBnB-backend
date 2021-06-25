from django.db import models

class User(models.Model):
    name        = models.CharField(max_length=45)
    birth       = models.DateField(null=True)
    email       = models.EmailField(null=True, max_length=45)
    password    = models.CharField(null=True, max_length=200)
    host        = models.BooleanField(default=0)
    provider_id = models.CharField(max_length=200)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    is_deleted  = models.BooleanField(default=0)

    class Meta:
        db_table = 'users'

class SocialFlatform(models.Model):
    provider_name = models.CharField(max_length=45)
    provider_id   = models.CharField(max_length=200)
    profile_image = models.URLField(max_length=2000)
    nick_name     = models.CharField(max_length=45)
    user          = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta: 
        db_table = 'social_flatform'