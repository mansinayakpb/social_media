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


# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ["id", "category_name", "description"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "category_name", "description"]

    def validate_category_name(self, value):
        if not value:
            raise serializers.ValidationError("Category name cannot be empty.")

        # Check if the value contains only alphabetic characters and spaces
        for char in value:
            if not (char.isalpha() or char.isspace()):
                raise serializers.ValidationError(
                    "Category name should only contain letters and spaces."
                )

        return value


class CommentSerializer(serializers.ModelSerializer):
    post_id = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), write_only=True, source="post"
    )

    class Meta:
        model = Comment
        fields = ["id", "comment", "post"]

    def create(self, validated_data):
        # Automatically assign the user when creating the comment
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image = serializers.ImageField(max_length=None, use_url=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = ["id", "title", "content", "image", "category", "user"]


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_following_email = serializers.EmailField(
        source="user_following", write_only=True
    )

    class Meta:
        model = Follow
        fields = [
            "id",
            "user",
            "user_following_email",
        ]

    def validate(self, data):
        """Ensure that the user cannot follow themselves or the same user twice."""
        user = self.context["request"].user
        # The email of the user being followed
        followed_user_email = data.get("user_following", None)

        # Check if the user is trying to follow themselves
        if user.email == followed_user_email:
            raise serializers.ValidationError("You cannot follow yourself!")

        # Check if the user is trying to follow the same user twice
        following_user = User.objects.filter(email=followed_user_email).first()
        if (
            following_user
            and Follow.objects.filter(
                user=user, user_following=following_user
            ).exists()
        ):
            raise serializers.ValidationError(
                "You are already following this user."
            )

        data["user_following"] = (
            following_user  # Assign the user instance to user_following
        )

        return data


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    post = serializers.StringRelatedField(read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), write_only=True, source="post"
    ) 

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
