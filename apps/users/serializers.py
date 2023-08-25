from typing import Any

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .exceptions import InvalidPasswordException
from .models import Address, Client, MagicLink


class AddressSerializer(serializers.ModelSerializer[Address]):
    class Meta:
        fields = (
            "timestamp",
            "name",
            "address1",
            "address2",
            "zip_code",
            "region",
            "city",
            "country",
        )


class ClientSerializer(serializers.ModelSerializer[Client]):
    address = AddressSerializer(read_only=True)

    class Meta:
        fields = ("email", "address")


class LoginSerializer(serializers.Serializer):
    method = serializers.ChoiceField(
        choices=(
            "password",
            "email",
        )
    )
    client = serializers.PrimaryKeyRelatedField[Client](queryset=Client.objects.all())
    password = serializers.CharField()

    def _validate_password(self, data):
        try:
            client = data["client"]

            if not client.check_password(data["password"]):
                raise InvalidPasswordException
        except (Client.DoesNotExist, InvalidPasswordException) as _:
            raise ValidationError("Invalid password or e-mail.")

    def _validate_email(self, data):
        try:
            # We get the magic link and delete it if found (since it was validated)
            MagicLink.objects.from_valid().get(
                client=data["client"], secret=data["password"]
            ).delete()
        except MagicLink.DoesNotExist as _:
            raise ValidationError("Invalid link.")

    def validate(self, attrs: Any) -> None:
        # TODO: Migrate to a separate validator
        match attrs["method"]:
            case "password":
                self._validate_password(attrs)
            case "email":
                self._validate_email(attrs)
            case _:
                raise ValidationError("Invalid Request", code=400)
