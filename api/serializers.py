from rest_framework import serializers

from api.models import Category, Comment, Follow, Like, Post, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


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
    # category = CategorySerializer(read_only=True)
    image = serializers.ImageField(max_length=None, use_url=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )  # Accept category ID for input

    class Meta:
        model = Post
        fields = ["id", "title", "content", "image", "category", "user"]


class FollowSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_followed = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = ["id", "user", "user_followed"]

    def validate(self, data):
        """Ensure user cannot follow themselves"""
        if self.context["request"].user == data["user_followed"]:
            raise serializers.ValidationError("you cannot follow yourself")
        return data


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "user", "post"]
