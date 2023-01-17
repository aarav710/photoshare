from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import ProfileListView, ProfileDetailView, PostListView, PostDetailView, CommentListView, LikeListView, FollowersListView, FollowingsListView, UserDetailView, LikeDetailView, CommentDetailView, FollowingsDetailView, RegisterView, FeedPostListView, ImageView
from rest_framework import routers
router = routers.DefaultRouter()

urlpatterns = [
    path('users/<int:user_id>/posts/', PostListView.as_view()),
    path('posts/<int:pk>/', PostDetailView.as_view()),
    path('posts/<int:post_id>/comments/', CommentListView.as_view()),
    path('comments/<int:comment_id>/', CommentDetailView.as_view()),
    path('posts/<int:post_id>/likes/', LikeListView.as_view()),
    path('likes/<int:like_id>/', LikeDetailView.as_view()),
    path('followings/users/<int:user_id>/', FollowingsListView.as_view()),
    path('followings/<int:follow_id>/', FollowingsDetailView.as_view()),
    path('followers/users/<int:user_id>/', FollowersListView.as_view()),
    path('users/profile/', ProfileListView.as_view()),
    path('users/profile/<int:user_id>/', ProfileDetailView.as_view()),
    path('users/', UserDetailView.as_view()),
    path('register/', RegisterView.as_view()),
    path('feed/', FeedPostListView.as_view()),
    path('images/', ImageView.as_view()),
]

urlpatterns += router.urls

#urlpatterns = format_suffix_patterns(urlpatterns)