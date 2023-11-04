import warnings
from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView

from rest_framework.views import APIView
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
        user = Client.objects.get(email=serializer.validated_data["email"])
        login(request, user)

        response = super(ClientLoginView, self).post(request, format=None)
        response.set_cookie("PST_TOKEN", response.data["token"], httponly=True)

        del response.data["token"]
        return response


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all().order_by('email')
    permission_classes = (ManageOnlyYourOwn,)
    lookup_field = 'email'

    def get_object(self):
        email = self.kwargs['email']
        warnings.warn(f"email: {email}")
        warnings.warn(f'kwargs: {self.kwargs}')
        return self.queryset.get(email=email)