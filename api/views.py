from django.utils.dateparse import parse_date
from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api.models import Category, Comment, Follow, Like, Post, User
from api.serializers import (CategorySerializer, CommentSerializer,
                             FollowSerializer, LikeSerializer, PostSerializer,
                             UserSerializer)

from .decorators import allow_any, is_admin_user, is_authenticated
from .pagination import CustomPagination
from .permissions import IsOwnerOrAdmin


class SignUpView(generics.CreateAPIView):
    serializer_class = UserSerializer

    @allow_any
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "Successfully created account.",
                    "id": user.id,
                    "email": user.email,
                }
            )
        return Response(
            {"message": "Error creating account.", "errors": serializer.errors}
        )


class LoginView(TokenObtainPairView):

    @allow_any
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response(
            {
                "refresh": response.data["refresh"],
                "access": response.data["access"],
                "message": "Successfully logged in",
            }
        )


class LogoutView(APIView):

    @allow_any
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out"})
        return Response({"detail": "Refresh token not provided"})


# Category Views


class CategoryListCreateView(generics.ListCreateAPIView):
    """Everyone can view categories, only admin can create them"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @allow_any  # Allows any user to perform GET requests
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @is_admin_user  # Only superusers can perform POST requests
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Save the category, admin only"""
        serializer.save()


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Only admin can update or delete categories"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @is_admin_user
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @is_admin_user
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


# Post Views

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = CustomPagination

    @is_authenticated
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Only the owner or admin can update/delete"""

    quryset = Post.objects.all()
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]


# Comment Views

class CommentListCreateView(generics.ListCreateAPIView):
    """List and create comments"""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    @is_authenticated
    def create(self, request, *args, **kwargs):
        """Save the comment with the current user as the owner"""
        post_id = self.request.data.get("post")
        post = Post.objects.get(id=post_id)
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=self.request.user, post=post)
            return Response(
                {
                    "message": "Comment created successfully.",
                    "comment": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "message": "Error creating comment.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    @is_authenticated
    def perform_update(self, serializer):
        """Only allow the comment owner to update it"""
        if (
            serializer.instance.user == self.request.user
            or self.request.user.is_staff
        ):
            serializer.save()
        else:
            return Response({"detail": "Permission Denied!!"})

    @is_authenticated
    def destroy(self, request, *args, **kwargs):
        """Get the comment instance"""
        instance = self.get_object()
        if instance.user == self.request.user or self.request.user.is_staff:
            instance.delete()
            return Response({"detail": "Comment deleted successfully!"})
        else:
            return Response(
                {"detail": "Permission Denied!!"},
                status=status.HTTP_403_FORBIDDEN,
            )


class PostCommentsListView(generics.ListAPIView):
    """Create an API to get all comments of a Post"""

    serializer_class = CommentSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        return Comment.objects.filter(post__id=post_id)


class UserCommentsListView(generics.ListAPIView):
    """Create an API to get all comments of a User"""

    serializer_class = CommentSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Comment.objects.filter(user__id=user_id)


class FollowCreateView(generics.CreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    @is_authenticated
    def perform_create(self, serializer):
        # Automatically assign the authenticated user to the 'user' field
        serializer.save(user=self.request.user)


class UserFollowersListView(generics.ListAPIView):
    """Create an API to get all followers of a User"""

    serializer_class = FollowSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.kwargs["user"]
        # Use `filter` and ensure to handle the case when no followers exist
        return Follow.objects.filter(user_following_id=user_id)


class LikeCreateView(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    @is_authenticated
    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        post = Post.objects.filter(id=post_id).first()

        if post is None:
            return Response(
                {"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer.save(user=self.request.user, post=post)


class PostLikeListView(generics.ListAPIView):
    """create an API to get the list of likes of a user post"""

    serializer_class = LikeSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        return Like.objects.filter(post=post_id)


class SearchAPIView(generics.GenericAPIView):
    filter_backends = [SearchFilter]

    def get(self, request):
        title = self.request.query_params.get("title")
        category = self.request.query_params.get("category")
        comment = self.request.query_params.get("comment")
        email = self.request.query_params.get("email")
        start_date = (
            parse_date(self.request.query_params.get("start_date"))
            if self.request.query_params.get("start_date")
            else None
        )
        end_date = (
            parse_date(self.request.query_params.get("end_date"))
            if self.request.query_params.get("end_date")
            else None
        )

        results = {
            "users": [],
            "posts": [],
            "comments": [],
            "category": [],
        }

        # Initialize queryset for posts and comments
        posts_queryset = Post.objects.all()
        comments_queryset = Comment.objects.all()

        # Filter posts based on parameters
        if title:
            posts_queryset = posts_queryset.filter(title__icontains=title)

        if category:
            posts_queryset = posts_queryset.filter(
                category__category_name__icontains=category
            )

        if start_date and end_date:
            posts_queryset = posts_queryset.filter(
                created_at__range=[start_date, end_date]
            )

        # Serialize filtered posts
        results["posts"] = PostSerializer(posts_queryset, many=True).data

        # Filter comments based on parameters
        if comment:
            comments_queryset = comments_queryset.filter(
                comment__icontains=comment
            )

        if start_date and end_date:
            comments_queryset = comments_queryset.filter(
                created_at__range=[start_date, end_date]
            )

        # Serialize filtered comments
        results["comments"] = CommentSerializer(
            comments_queryset, many=True
        ).data

        # Filter users based on email
        if email:
            users = User.objects.filter(email__icontains=email)
            results["users"] = UserSerializer(users, many=True).data

        return Response(results)
