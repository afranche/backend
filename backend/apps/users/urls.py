from django.urls import path, include
from rest_framework import routers
from .views import ClientViewSet, ClientLoginView, PongView

router = routers.DefaultRouter()
router.register(r'client', ClientViewSet)

urlpatterns = [
    path("login/", ClientLoginView.as_view(), name="client-login-view"),
    path("pong/", PongView.as_view(), name="client-pong-view"),
] + router.urls