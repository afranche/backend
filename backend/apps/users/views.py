from logging import warn
import warnings
import copy
from django.contrib.auth import login
from django.conf import settings
from django.db.models import Q
from knox.views import LoginView as KnoxLoginView

from rest_framework.views import APIView, Http404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets

from apps.users.models import Client

from apps.users.permissions import ManageOnlyYourOwn

from .serializers import ClientSerializer, LoginSerializer


class PongView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        return Response("Pong batard")


class ClientLoginView(KnoxLoginView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = Client.objects.get(email=serializer.validated_data["email"])  # type: ignore
        login(request, user)

        response = super(ClientLoginView, self).post(request, format=None)
        response.set_cookie(
            "PST_TOKEN",
            copy.deepcopy(response.data["token"]),  # type: ignore
            expires=response.data["expiry"],  # type: ignore
            secure=not settings.DEBUG,
            httponly=True,
            samesite="Strict",
        )

        del response.data["token"]  # type: ignore
        return response


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all().order_by("email")
    permission_classes = (ManageOnlyYourOwn,)
    lookup_field = "email"

    def get_object(self):
        if email := self.kwargs.get("email"):
            # FIXME(adina): should only fetch using email (and not id!)
            if item := self.queryset.filter(Q(email=email) | Q(id=email)).first():
                return item

        warn(f'Attempting to find user with email {self.kwargs.get("email")}')
        raise Http404("Cannot find user")
