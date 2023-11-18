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


#FIXME(adina): tests are broken
class ManageOnlyYourOwn(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):

        logging.warn(f'user {request.user} is staff ? {request.user.is_staff}')

        if request.user.is_staff:
            return True

        logging.warn(f'user: {request.user} == {obj} ?')

        if hasattr(obj, 'user'):
            return obj.user == request.user

        logging.warn(f'{type(obj)} ({obj}) does not have "user" property. Permission will never be granted')
        return obj == request.user
