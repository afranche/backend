from knox.auth import TokenAuthentication
from rest_framework import exceptions

from django.utils.translation import gettext_lazy as _


class CookieTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        if "PST_TOKEN" not in request.COOKIES:
            return None

        cookie_token = request.COOKIES["PST_TOKEN"]

        user, auth_token = self.authenticate_credentials(cookie_token.encode("utf-8"))
        return (user, auth_token)
