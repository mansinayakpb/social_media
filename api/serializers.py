from rest_framework import serializers

from api.models import Category, Comment, Follow, Like, Post, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "category_name", "description"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "comment", "user", "post"]


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "title", "content", "image", "category", "user"]


class FollowSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_followed = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "user", "user_followed"]


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "user", "post"]
