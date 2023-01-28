from django.shortcuts import render
from rest_framework.views import APIView
from django.http import Http404
from django.core.exceptions import BadRequest
from .models import Post, Comment, Like, Profile, Followers
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, FollowersSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from .authentication import UserAuthentication
from django.db.models import Count
from django.db.models.query import QuerySet
from .image_service import image_services3

# Create your views here.


class PostListView(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request: Request, user_id, format=None) -> Response:
        if user_id is None:
            raise Http404
        # returns all posts by user_id along with likes and comments count
        posts: 'QuerySet[Post]' = Post.objects.filter(user__id=user_id)\
            .annotate(likes_count=Count('like'))\
            .annotate(comments_count=Count('comment'))\
            .order_by('-date_created')
        posts_response = PostSerializer(posts, many=True)
        return Response(posts_response.data)

    def post(self, request, user_id, format=None):
        user = request.user
        post_request = PostSerializer(data={**request.data}, context={'user': user})
        if post_request.is_valid():
            post_request.save()
            return Response({**post_request.data,
                             'likes_count': 0,
                             'comments_count': 0},
                            status=status.HTTP_201_CREATED)
        return Response(post_request.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk, format=None):
        try:
            post: Post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404
        post.likes_count = post.like_set.count()
        post.comments_count = post.comment_set.count()
        post_response = PostSerializer(post)
        return Response(post_response.data)

    def delete(self, request, pk, format=None):
        auth_user: User = request.user
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404
        user = post.user
        uid = user.profile.uid
        if uid != auth_user.profile.uid:
            raise PermissionDenied
        post.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, format=None):
        auth_user = request.user
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404
        user = post.user
        uid = user.profile.uid
        if uid != auth_user.profile.uid:
            raise PermissionDenied

        serializer = PostSerializer(post, data=request.data)
        likes_count = post.like_set.count()
        comments_count = post.comment_set.count()
        if serializer.is_valid():
            serializer.save()
            return Response({**serializer.data,
                             'comments_count': comments_count,
                             'likes_count': likes_count},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedPostListView(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        user: User = request.user
        followers: 'QuerySet[Followers]' = Followers.objects.filter(follower__pk=user.pk)
        followings = list(map(lambda x: x.following, followers))
        followings_id = list(map(lambda x: x.pk, followings))
        posts = Post.objects.filter(user__pk__in=followings_id).annotate(likes_count=Count('like'), comments_count=Count('comment')).order_by('-date_created')
        posts_response = PostSerializer(posts, many=True)
        return Response(posts_response.data)


class CommentListView(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, post_id, format=None):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise Http404
        comments = post.comment_set.all()
        comments_response = CommentSerializer(comments, many=True)
        return Response(comments_response.data)

    def post(self, request, post_id, format=None):
        user = request.user
        post = Post.objects.get(pk=post_id)

        comment = CommentSerializer(data={**request.data, 'user': user, 'post': post})
        if comment.is_valid():
            comment.save()
            return Response(comment.data, status=status.HTTP_201_CREATED)
        return Response(comment.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request: Request, comment_id, format=None) -> Response:
        auth_user: User = request.user
        try:
            comment: Comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            raise Http404
        user: User = comment.user
        uid: str = user.profile.uid
        if uid != auth_user.profile.uid:
            raise PermissionDenied
        comment.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LikeListView(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request: Request, post_id, format=None) -> Response:
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise Http404

        likes = post.like_set.all()
        likes_response = LikeSerializer(likes, many=True)
        return Response(likes_response.data)

    def create(self, request, post_id, format=None):
        user = request.user
        post = Post.objects.get(pk=post_id)

        like = LikeSerializer(data={**request.data, 'post': post, 'user': user})
        if like.is_valid():
            like.save()
            return Response(like.data, status=status.HTTP_201_CREATED)
        return Response(like.errors, status=status.HTTP_400_BAD_REQUEST)


class LikeDetailView(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, like_id, format=None):
        auth_user: User = request.user
        try:
            like = Like.objects.get(pk=like_id)
        except Like.DoesNotExist:
            raise Http404
        user = like.user
        uid = user.profile.uid
        if uid != auth_user.profile.uid:
            raise PermissionDenied
        like.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class FollowersListView(APIView):
    def get(self, request, user_id, format=None):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404

        followers = user.follower_set.all()
        followers_response = FollowersSerializer(followers, many=True)
        return Response(followers_response.data)


class FollowingsListView(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, user_id, format=None):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404

        followings = user.following_set.all()
        followings_response = FollowersSerializer(followings, many=True)
        return Response(followings_response.data)

    def create(self, request, user_id, format=None):
        uid = request.user
        try:
            following = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404

        follower = User.objects.get(pk=user_id)
        serializer = FollowersSerializer(data={**request.data, 'following': following, 'follower': follower})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowingsDetailView(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, follow_id, format=None):
        uid = request.user
        try:
            user = User.objects.get(profile__uid=uid)
        except User.DoesNotExist:
            raise Http404
        follow = Followers.objects.get(pk=follow_id)
        if follow.follower.id != user.id:
            return PermissionDenied
        follow.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class ProfileListView(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request: Request, format=None) -> Response:
        username: str = self.request.query_params.get('username')
        if username is None:
            username = ''
        users: 'QuerySet[User]' = User.objects.filter(username__contains=username)
        profiles_response = UserSerializer(users, many=True)
        return Response(profiles_response.data)

    def put(self, request: Request, format=None) -> Response:
        user = request.user

        serializer: UserSerializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailView(APIView):
    def get(self, request: Request, user_id, format=None) -> Response:
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404
        profile_response = UserSerializer(user)
        return Response(profile_response.data)


class UserDetailView(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, format=None) -> Response:
        user = request.user

        user_response = UserSerializer(user)
        return Response(user_response.data)


class RegisterView(APIView):
    def post(self, request: Request, format=None) -> Response:
        serializer: UserSerializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ImageView(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, format=None) -> Response:
        try:
            url_response = image_services3.generate_pre_signed_url()
        except Exception as e:
            raise BadRequest
        return Response({'data': url_response}, status=status.HTTP_201_CREATED)