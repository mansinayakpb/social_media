from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Category, Comment, Follow, Like, Post, Profile, User

# Register your models here.


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "is_staff", "is_active", "date_joined")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "profile_picture",
        "birth_date",
        "location",
        "gender",
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "user_followed")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created_at")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "comment", "created_at")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category_name", "description")