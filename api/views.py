from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api.models import Category, Comment, Follow, Post
from api.permissions import IsOwnerOrAdmin
from api.serializers import (CategorySerializer, CommentSerializer,
                             FollowSerializer, PostSerializer, UserSerializer)


class SignUpView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
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
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

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

    def get_permissions(self):
        """Assign permissions based on the request method"""
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        """Save the category, admin only"""
        serializer.save()


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Only admin can update or delete categories"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


# Post Views


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        """Save the post with the current user as the owner"""
        serializer.save(user=self.request.user)


class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Only the owner or admin can update/delete"""

    quryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


# Comment Views


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def comment_create(self, serializer):
        """Save the comment with the current user as the owner"""
        serializer.save(user=self.request.user)


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def update(self, serializer):
        """Only allow the comment owner to update it"""
        if serializer.instance.user == self.request.user or self.request.user.is_staff:
            serializer.save()
        else:
            return Response({"detail": "Permission Denied!!"})

    def destroy(self, instance):
        if instance.user == self.request.user or self.request.user.is_staff:
            instance.delete()
        else:
            return Response({"detail": "Permission Denied!!"})


class PostCommentsListView(generics.ListAPIView):
    """Create an API to get all comments of a Post"""

    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        return Comment.objects.filter(post__id=post_id)


class UserCommentsListView(generics.ListAPIView):
    """Create an API to get all comments of a User"""

    serializer_class = CommentSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Comment.objects.filter(user__id=user_id)


class UserFollowersListView(generics.ListAPIView):
    """Create an API to get all followers of a User"""

    serializer_class = FollowSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Follow.objects.filter(user_follower_id=user_id)
