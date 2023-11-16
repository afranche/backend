import sys
import warnings
from rest_framework import permissions
import logging

class IsAdminOrReadOnly(permissions.IsAdminUser):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if the user is an admin for write/delete actions.
        return super().has_permission(request, view)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class ManageOnlyYourOwn(permissions.BasePermission):
    def has_permission(self, request, view):
        warnings.warn(f"{request.method}")

        if request.method == "POST" or request.user.is_staff:
            # Allow creation (POST) for all or any action for admin users.
            return True
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return False  # Deny all other non-admin users for other actions (GET, PUT, DELETE).

    def has_object_permission(self, request, view, obj):
        warnings.warn(f'coucou {request.user} {obj.user}')
        if request.user.is_staff:
            # Admin users have full permissions on the object.
            return True


            # Normal users can only update or delete their own objects.
        warnings.warn(f'obj.user == request.user {obj.user == request.user} {obj} {obj.user} {request.user}')
        print("obj.user == request.user", obj.user == request.user, file=sys.stderr)
        print(obj, obj.user, request.user, file=sys.stderr)
        return obj.user == request.user
