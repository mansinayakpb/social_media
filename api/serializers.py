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
    post = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ["id", "comment", "user", "post"]


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image = serializers.ImageField(max_length=None, use_url=True)
    category = serializers.StringRelatedField()  # Accept category ID for input

    class Meta:
        model = Post
        fields = ["id", "title", "content", "image", "category", "user"]


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_following = serializers.StringRelatedField()

    class Meta:
        model = Follow
        fields = [
            "id",
            "user",
            "user_following",
        ]  # Changed user_followed to user_following

    def validate(self, data):
        """Ensure that the user cannot follow themselves or the same user twice."""
        user = self.context["request"].user
        # The user being followed
        followed_user_email = data.get("user_following")

        # Check if the user trying to follow itself
        if user.email == followed_user_email:
            raise serializers.ValidationError("You cannot follow yourself!")

        # Check if the user trying to follow the same user twice
        if Follow.objects.filter(
            user=user, user_following__email=followed_user_email
        ).exists():
            raise serializers.ValidationError(
                "You are already following this user."
            )

        return data


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    # Read-only representation of the post
    post = serializers.StringRelatedField(read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), write_only=True, source="post"
    )  # Write-only representation of the post

    class Meta:
        model = Like
        fields = ["id", "user", "post", "post_id"]

    def validate(self, data):
        """Ensure that the user cannot like the same post twice."""
        # Get the current authenticated user
        user = self.context["request"].user
        # Retrieve post from the data
        post = data.get("post")

        # Check if the user has already liked this post
        if Like.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError(
                "You have already liked this post."
            )

        return data
