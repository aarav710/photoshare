from rest_framework import serializers
from .models import Profile, Comment, Post, Like, Followers
from django.contrib.auth.models import User
from .authentication import authentication_service

class ProfileSerializer(serializers.ModelSerializer):

    class Meta():
        model = Profile
        fields = ['id', 'date_created', 'bio', 'photo_url']
        read_only_fields = ['date_created']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True, many=False)

    class Meta():
        model = User
        fields = ['id', 'profile', 'username', 'email', 'date_joined', 'password']
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['date_created']
        depth = 1

    def create(self, validated_data):
        user = authentication_service.create_new_user({'email': validated_data['email'],
                                                       'password': validated_data['password'],
                                                       'display_name': validated_data['username']})
        uid = user.uid
        user = User(username=user.display_name, password=validated_data['password'], email=user.email)
        # check for errors here, if any error delete record from firebase
        user.save()
        Profile.objects.create(uid=uid, user=user)
        return user

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=False)

    class Meta():
        model = Comment
        fields = ['id', 'text', 'date_created', 'user']
        depth = 1
        read_only_fields = ['date_created', 'user']

    def create(self, validated_data):
        user = validated_data.pop('user')
        post = validated_data.pop('post')
        comment = Comment.objects.create(**validated_data, user=user, post=post)
        return comment


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=False)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta():
        model = Post
        fields = ['id', 'photo_url', 'caption', 'date_created', 'user', 'likes_count', 'comments_count']
        read_only_fields = ['date_created', 'likes_count', 'comments_count', 'user']
        depth = 1

    def create(self, validated_data):
        user = self.context['user']
        post = Post.objects.create(**validated_data, user=user)
        return post

class FollowersSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True, many=False)
    following = UserSerializer(read_only=True, many=False)

    class Meta():
        model = Followers
        fields = ['id', 'date_created', 'follower', 'following']
        read_only_fields = ['date_created']
        depth = 1

    def create(self, validated_data):
        follower = validated_data.pop('follower')
        following = validated_data.pop('following')
        follow = Followers.objects.create(**validated_data, follower=follower, following=following)
        return follow


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=False)

    class Meta():
        model = Like
        fields = ['id', 'date_created', 'user']
        read_only_fields = ['date_created']
        depth = 1

    def create(self, validated_data):
        user = validated_data.pop('user')
        post = validated_data.pop('post')
        like = Like.objects.create(**validated_data, user=user, post=post)
        return like

