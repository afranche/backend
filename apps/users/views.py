from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import LoginSerializer


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
        user = serializer.validated_data["client"]
        login(request, user)

        response = super(ClientLoginView, self).post(request, format=None)
        response.set_cookie("PST_TOKEN", response.data["token"], httponly=True)

        del response.data["token"]
        return response
