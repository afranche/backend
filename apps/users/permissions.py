from rest_framework import permissions
import logging

class IsAdminOrReadOnly(permissions.IsAdminUser):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if the user is an admin for write/delete actions.
        return super().has_permission(request, view)