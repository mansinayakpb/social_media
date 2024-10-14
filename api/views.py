from django.utils.dateparse import parse_date
from rest_framework import generics, status
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

from .decorators import (allow_any, is_admin_user, is_authenticated,
                         is_owner_or_admin)
from .pagination import CustomPagination
from rest_framework.permissions import IsAuthenticated


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


# class CategoryView(generics.GenericAPIView):
#     """Manage categories: view (anyone), create, update, delete (admin only)"""

#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer

#     @allow_any
#     def get(self, request, *args, **kwargs):
#         if "pk" in kwargs:
#             return self.retrieve(request, *args, **kwargs)
#         return self.list(request, *args, **kwargs)

#     @is_admin_user
#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)

#     @is_admin_user
#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)

#     @is_admin_user
#     def patch(self, request, *args, **kwargs):
#         return self.partial_update(request, *args, **kwargs)

#     @is_admin_user
#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)

#     def list(self, request, *args, **kwargs):
#         serializer = self.get_serializer(self.get_queryset(), many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, *args, **kwargs):
#         serializer = self.get_serializer(self.get_object())
#         return Response(serializer.data)

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def update(self, request, *args, **kwargs):
#         serializer = self.get_serializer(
#             self.get_object(), data=request.data, partial=False
#         )
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def partial_update(self, request, *args, **kwargs):
#         serializer = self.get_serializer(
#             self.get_object(), data=request.data, partial=True
#         )
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def destroy(self, request, *args, **kwargs):
#         self.get_object().delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryView(generics.GenericAPIView):
    """Manage categories: view (anyone), create, update, delete (admin only)"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @allow_any
    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)    

    @is_admin_user
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return self.create(request, *args, **kwargs)

    @is_admin_user
    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=False)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)        
        return self.update(request, *args, **kwargs)    

    @is_admin_user
    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return self.partial_update(request, *args, **kwargs)

    @is_admin_user
    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)


# Post Views


class PostView(generics.GenericAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        # Let the parent class handle the post request
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @is_owner_or_admin
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @is_owner_or_admin
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"detail": "Post deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )

    def get(self, request, *args, **kwargs):

        post_id = kwargs.get("pk")
        if post_id:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# class PostListCreateView(generics.ListCreateAPIView):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer
#     parser_classes = [MultiPartParser, FormParser]
#     pagination_class = CustomPagination

#     @is_authenticated
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)


# class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#     """Only the owner or admin can update/delete"""

#     quryset = Post.objects.all()
#     serializer_class = PostSerializer
#     parser_classes = [MultiPartParser, FormParser]

#     @is_owner_or_admin
#     @is_authenticated
#     def perform_update(self, serializer):
#         serializer.save(user=self.request.user)

#     def delete(self, request, *args, **kwargs):
#         object = self.get_object()
#         object.delete()
#         return Response({"detail": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)


# Comment Views


class CommentView(generics.GenericAPIView):
    """Manage comments: list, create, update, delete"""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Create a comment with the current user as the owner"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
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

    def put(self, request, *args, **kwargs):
        """Update a comment"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        if serializer.is_valid():
            if instance.user == request.user or request.user.is_staff:
                serializer.save()
                return Response(
                    {
                        "message": "Comment updated successfully.",
                        "comment": serializer.data,
                    }
                )
            else:
                return Response(
                    {"detail": "Permission Denied!"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """Delete a comment"""
        instance = self.get_object()
        if instance.user == request.user or request.user.is_staff:
            instance.delete()
            return Response(
                {"message": "Comment deleted successfully!"},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"detail": "Permission Denied!"}, status=status.HTTP_403_FORBIDDEN
        )

    def get_queryset(self):
        """Retrieve comments based on post_id or user_id"""
        post_id = self.kwargs.get("post_id")
        user_id = self.kwargs.get("user_id")

        if post_id:
            return Comment.objects.filter(post__id=post_id)
        elif user_id:
            return Comment.objects.filter(user__id=user_id)
        return Comment.objects.none()

    def get(self, request, *args, **kwargs):
        """List comments for a specific post or user"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FollowView(generics.GenericAPIView):
    """Create a follow and list all followers of a user"""

    serializer_class = FollowSerializer
    queryset = Follow.objects.all()
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Handles creating a follow relationship"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        """Handles listing all followers of a user"""
        queryset = self.get_queryset()  # Get the queryset based on the user
        page = self.paginate_queryset(queryset)  # Paginate the queryset

        if page is not None:
            serializer = self.get_serializer(
                page, many=True
            )  # Serialize paginated data
            return self.get_paginated_response(
                serializer.data
            )  # Return paginated response

        serializer = self.get_serializer(
            queryset, many=True
        )  # Serialize all data if no pagination
        return Response(serializer.data) 

    def get_queryset(self):
        """Retrieve all followers for a specific user"""
        user_id = self.kwargs.get("user")  
        return Follow.objects.filter(
            user_following_id=user_id
        )  


class LikeView(generics.GenericAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Create a like for the post"""
        serializer = self.get_serializer(data=request.data)
        post_id = self.kwargs.get("post_id")
        post = Post.objects.filter(id=post_id).first()

        if post is None:
            return Response(
                {"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if serializer.is_valid():
            serializer.save(user=self.request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """Retrieve all likes for a specific post"""
        post_id = self.kwargs.get("post_id")
        return Like.objects.filter(post=post_id)

    def get(self, request, *args, **kwargs):
        """List comments for a specific post or user"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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


class ProfileCreateView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "id": user.id,
                    "email": user.email,
                    "message": "User created successfully"
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
