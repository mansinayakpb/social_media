from functools import wraps

from rest_framework import status
from rest_framework.response import Response


def is_admin_user(func):
    @wraps(func)
    def inner(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(
                {"detail": "Only superusers can perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return func(self, request, *args, **kwargs)

    return inner


def allow_any(func):
    @wraps(func)
    def inner(self, request, *args, **kwargs):
        return func(self, request, *args, **kwargs)

    return inner


def is_authenticated(func):
    @wraps(func)
    def inner(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication is required to view this content."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return func(self, request, *args, **kwargs)

    return inner


def is_owner_or_admin(func):
    @wraps(func)
    def inner(self, request, *args, **kwargs):
        obj = kwargs.get(
            "obj"
        )  # Assuming you pass the object to check ownership
        if obj and (
            request.user != obj.owner and not request.user.is_superuser
        ):
            return Response(
                {
                    "detail": "You do not have permission to perform this action."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return func(self, request, *args, **kwargs)

    return inner
