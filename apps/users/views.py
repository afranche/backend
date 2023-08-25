from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView

from .serializers import LoginSerializer


class ClientLoginView(KnoxLoginView):
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["client"]
        login(request, user)
        return super(LoginView, self).post(request, format=None)
