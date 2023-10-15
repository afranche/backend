from rest_framework import permissions
import logging

class IsAdminOrReadOnly(permissions.IsAdminUser):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if the user is an admin for write/delete actions.
        return super().has_permission(request, view)


class ManageOnlyYourOwn(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST" or request.user.is_staff:
            # Allow creation (POST) for all or any action for admin users.
            return True

        return False  # Deny all other non-admin users for other actions (GET, PUT, DELETE).

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            # Admin users have full permissions on the object.
            return True

        if request.method in ["PUT", "PATCH", "DELETE"]:
            # Normal users can only update or delete their own objects.
            return obj.user == request.user

        return False  # Deny all other actions for non-admin users.