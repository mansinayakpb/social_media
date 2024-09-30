from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from api.views import (
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    CommentListCreateView,
    CommentRetrieveUpdateDestroyView,
    FollowCreateView,
    LikeCreateView,
    LoginView,
    LogoutView,
    PostCommentsListView,
    PostLikeListView,
    PostListCreateView,
    PostRetrieveUpdateDestroyView,
    SearchAPIView,
    SignUpView,
    UserCommentsListView,
    UserFollowersListView,
)

urlpatterns = [
    # JWT
    path(
        "api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Category URLs
    path(
        "categories/",
        CategoryListCreateView.as_view(),
        name="category_list_create",
    ),
    path(
        "categories/<uuid:pk>/",
        CategoryRetrieveUpdateDestroyView.as_view(),
        name="category_detail",
    ),
    # Post URLs
    path("posts/", PostListCreateView.as_view(), name="post_list_create"),
    path(
        "posts/<uuid:pk>/",
        PostRetrieveUpdateDestroyView.as_view(),
        name="post_detail",
    ),
    # Comment URLs
    path(
        "comments/",
        CommentListCreateView.as_view(),
        name="comment_list_create",
    ),
    path(
        "comments/<uuid:pk>/",
        CommentRetrieveUpdateDestroyView.as_view(),
        name="comment_detail",
    ),
    path(
        "posts/<uuid:post_id>/comments/",
        PostCommentsListView.as_view(),
        name="post_comments",
    ),
    path(
        "users/<uuid:user_id>/comments/",
        UserCommentsListView.as_view(),
        name="user_comments",
    ),
    path(
        "users/<uuid:user_id>/followers/",
        UserFollowersListView.as_view(),
        name="user_followers",
    ),
    path("follow/", FollowCreateView.as_view(), name="follower"),
    path(
        "posts/<uuid:post_id>/like/",
        LikeCreateView.as_view(),
        name="like-create",
    ),
    path(
        "posts/<uuid:post_id>/likes/",
        PostLikeListView.as_view(),
        name="likepost_list",
    ),
    path("search/", SearchAPIView.as_view(), name="search_filter"),
]
