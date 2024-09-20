import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from api.managers import CustomUserManager


class TimesStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class User(AbstractUser, TimesStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Profile(TimesStampedModel):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    profile_picture = models.ImageField(
        upload_to="post_media/", blank=True, null=True
    )
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(
        max_length=200, choices=GENDER_CHOICES, blank=True, null=True
    )

    def __str__(self):
        return self.user.email


class Follow(TimesStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    user_followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followed"
    )

    class Meta:
        unique_together = ("user", "user_followed")

    def __str__(self):
        return f"{self.user.email} follow {self.user_followed.email}"


class Category(TimesStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.category_name


class Post(TimesStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to="post_media/", null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="posts"
    )
    user = models.ForeignKey(
        User, related_name="post", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title


class Like(TimesStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="like_post"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="like_by_user"
    )

    class Meta:
        unique_together = ("post", "user")

    def __str__(self):
        return f"{self.user} likes {self.post.title}"


class Comment(TimesStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post, related_name="comment", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_comments"
    )
    comment = models.TextField(max_length=255)

    def __str__(self):
        return self.comment
