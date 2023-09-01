from django.urls import path

from .views import ClientLoginView, PongView


urlpatterns = (
    path("login/", ClientLoginView.as_view(), name="client-login-view"),
    path("pong/", PongView.as_view(), name="client-pong-view"),
)
