import datetime

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Post(models.Model):
    photo_url = models.URLField(blank=True)
    caption = models.CharField(max_length=150)
    date_created = models.DateField(default=datetime.date.today)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Comment(models.Model):
    text = models.CharField(max_length=100)
    date_created = models.DateField(default=datetime.date.today)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Like(models.Model):
    date_created = models.DateField(default=datetime.date.today)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Followers(models.Model):
    date_created = models.DateField(default=datetime.date.today)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_created = models.DateField(default=datetime.date.today)
    uid = models.CharField(max_length=200, default='')
    bio = models.CharField(max_length=150, default='')
    photo_url = models.URLField(max_length=500, default='')

