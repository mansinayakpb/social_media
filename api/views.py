# from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils.dateparse import parse_date
from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api.models import Category, Comment, Follow, Like, Post, User
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    FollowSerializer,
    LikeSerializer,
    PostSerializer,
    UserSerializer,
)

from .permissions import IsOwnerOrAdmin
from .pagination import CustomPagination


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
    pagination_class = CustomPagination
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = PostFilter

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

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]


# Comment Views


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = CommentFilter

    def perform_create(self, serializer):
        """Save the comment with the current user as the owner"""
        post_id = self.request.data.get("post")
        post = Post.objects.get(id=post_id)
        serializer.save(user=self.request.user, post=post)


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        """Only allow the comment owner to update it"""
        if (
            serializer.instance.user == self.request.user
            or self.request.user.is_staff
        ):
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


# class FollowCreateView(generics.CreateAPIView):
#     # queryset = Follow.objects.all()
#     # serializer_class = FollowSerializer
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user_following_email = request.POST.get(
#             "user_following_email"
#         )  # this is string
#         user = request.user  # this is user object
#         user_follow = Follow.objects.create(
#             user=user, user_following=user_following
#         )

#         # Check if the email was provided
#         if not user_following_email:
#             return Response({"msg": "Provide Email!"})

#         user_following = User.objects.filter(
#             email=user_following_email
#         ).first()

#         # Check if the user exists
#         if not user_following:
#             return Response({"msg": "No User Found with this Email!"})

#         # check if the user trying to follow themselves
#         if request.user == user_following:
#             return Response({"msg": "you cannot follow yourself!"})

#         # check if the person following the same person twice
#         if Follow.objects.filter(
#             user=request.user, user_following=user_following
#         ).exists():
#             return Response({"msg": "you are already following the user"})

#         return Response(
#             {
#                 "msg": f"you are now following {user_following.email}",
#                 "data": {
#                     "id": (user_follow.id),
#                     "user": request.user.email,
#                     "user_following": user_following.email,
#                 },
#             }
#         )


class FollowCreateView(generics.CreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        post = Post.objects.filter(id=post_id).first()

        if post is None:
            return Response({"detail": "Post not found."})

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
        title = self.request.query_params.get("title", None)
        category = self.request.query_params.get("category", None)
        comment = self.request.query_params.get("comment", None)
        email = self.request.query_params.get("email", None)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)

        results = {"users": [], "posts": [], "comments": [], "category": []}

        start_date = parse_date(start_date) if start_date else None
        end_date = parse_date(end_date) if end_date else None

        if title:
            posts = Post.objects.filter(title__icontains=title)
            serializer = PostSerializer(posts, many=True)
            results['posts'] = serializer.data

        if category:
            posts = Post.objects.filter(category__category_name__icontains=category)
            serializer = PostSerializer(posts, many=True)
            results['posts'] = serializer.data

        if start_date and end_date:
            posts = Post.objects.filter(created_at__range=[start_date, end_date])
            results['posts'] = PostSerializer(posts, many=True).data
             
        if comment:
            comments = Comment.objects.filter(comment__icontains=comment)
            serializer = CommentSerializer(comments, many=True)
            results['comments'] = serializer.data

        # if start_date:
        #     comments = Comment.objects.filter(created_at__date=[start_date])
        #     results['comments'] = CommentSerializer(comments, many=True).data

        if email:
            users = User.objects.filter(email__icontains=email)
            serializer = UserSerializer(users, many=True)
            results['users'] = serializer.data

        return Response(results)


# class SearchAPIView(generics.GenericAPIView):
#     def get(self, request):
#         title = request.query_params.get("title", None)
#         category = request.query_params.get("category", None)
#         comment = request.query_params.get("comment", None)
#         email = request.query_params.get("email", None)

#         results = {"users": [], "posts": [], "comments": []}

#         # Filter posts by title or category (separately)
#         if title:
#             posts = Post.objects.filter(title__icontains=title)
#             results['posts'] = PostSerializer(posts, many=True).data
#         elif category:
#             posts = Post.objects.filter(category__category_name__icontains=category)
#             results['posts'] = PostSerializer(posts, many=True).data

#         # Filter comments by comment content
#         if comment:
#             comments = Comment.objects.filter(comment__icontains=comment)
#             results['comments'] = CommentSerializer(comments, many=True).data

#         # Filter users by email
#         if email:
#             users = User.objects.filter(email__icontains=email)
#             results['users'] = UserSerializer(users, many=True).data

#         return Response(results)
