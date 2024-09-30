from rest_framework import permissions

# class IsOwnerOrAdmin(permissions.BasePermission):
#     """
#     Custom permission to only allow owners of a post or
#     admins to edit or delete it.
#     """

#     def has_permission(self, request, view):
#         # Allow any authenticated user to read
#         return request.user and request.user.is_authenticated
    
#     def has_object_permission(self, request, view, obj):


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a post or admins to edit or delete it.
    """

    def has_permission(self, request, view):
        # Allow any authenticated user to read
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow read permissions to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # write(PUT, PATCH, DELETE) permission are only allowed to the owner or admin
        return obj.user == request.user or request.user.is_staff

