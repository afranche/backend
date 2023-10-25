from typing import Any

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .exceptions import InvalidPasswordException
from .models import Address, Client, MagicLink


class AddressSerializer(serializers.ModelSerializer[Address]):
    class Meta:
        model = Address
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
    groups = serializers.SerializerMethodField()

    def get_groups(self, obj: Client):
        return obj.groups.values_list("name", flat=True)

    class Meta:
        model = Client
        fields = ("email", "address", "is_staff", "groups")

class ClientCreationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Client
        fields = ["email", "password1", "password2", "address"]
    
    def validate(self, attrs: Any) -> Any:
        if attrs["password1"] != attrs["password2"]:
            raise ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data: Any) -> Client:
        validated_data.pop("password2")
        password = validated_data.pop("password1")
        if "address" in validated_data:
            address = Address.objects.create(**validated_data.pop("address"))
        else:
            address = None
        client = Client.objects.create(address=address, **validated_data)
        client.set_password(password)
        client.save()
        return client

class ClientChangeSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Client
        fields = ["email", "address"]

class LoginSerializer(serializers.Serializer):
    method = serializers.ChoiceField(
        choices=(
            "password",
            "email",
        )
    )
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
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

    def validate(self, attrs: Any) -> Any:
        # TODO: Migrate to a separate validator
        match attrs["method"]:
            case "password":
                self._validate_password(attrs)
            case "email":
                self._validate_email(attrs)
            case _:
                raise ValidationError("Invalid Request", code=400)
        return attrs
