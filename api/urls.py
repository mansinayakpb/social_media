from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from api.views import (
    CategoryView,
    CommentView,
    FollowView,
    LikeView,
    LoginView,
    LogoutView,
    PostView,
    ProfileCreateView,
    SearchAPIView,
    SignUpView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="API Docs",
        default_version="v1",
        description="Author Registration",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@xyz.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
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
    # To list all categories or create a new one
    path("categories/", CategoryView.as_view(), name="category_list_create"),
    # To retrieve, update, or delete a specific category
    path(
        "categories/<uuid:pk>/",
        CategoryView.as_view(),
        name="category_detail_update_delete",
    ),
    # Post URLs
    path("posts/", PostView.as_view(), name="post_list_create"),
    path(
        "posts/<uuid:pk>/",
        PostView.as_view(),
        name="post_detail",
    ),
    # Comment URLs
    # To create a comment
    path("comments/", CommentView.as_view(), name="create_comment"),
    # To list comments for a specific post
    path(
        "comments/<uuid:post_id>/",
        CommentView.as_view(),
        name="list_comments_for_post",
    ),
    # To update or delete a specific comment
    path(
        "comments/<uuid:post_id>/<uuid:pk>/",
        CommentView.as_view(),
        name="update_delete_comment",
    ),
    # Follow URLs
    # To create a follow relationship
    path("follow/", FollowView.as_view(), name="create_follow"),
    # To list all followers of a user
    path("follow/<uuid:user>/", FollowView.as_view(), name="list_followers"),
    # Like URLs
    # To create a like for a post
    path("post/<uuid:post_id>/like/", LikeView.as_view(), name="create_like"),
    # To list all likes for a post
    path("post/<uuid:post_id>/likes/", LikeView.as_view(), name="list_likes"),
    # Filter
    path("search/", SearchAPIView.as_view(), name="search_filter"),
    path("profile/", ProfileCreateView.as_view(), name="user_profile"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
