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

    class Meta:
        model = Client
        fields = ("email", "address", "is_active", "is_staff")

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
            "email_from_magic_link",
        )
    )
    email = serializers.EmailField()
    password = serializers.CharField()  # Is either password or secret from magic link

    def _validate_password(self, data):
        try:
            email = data["email"]
            password = data["password"]
            client = Client.objects.get(email=email)
            
            if not client.check_password(password):
                raise InvalidPasswordException
        except (Client.DoesNotExist, InvalidPasswordException) as _:
            raise ValidationError("Invalid password or email.")

    def _validate_email_from_magic_link(self, data):
        try:
            # We get the magic link and delete it if found (since it was validated)
            MagicLink.objects.from_valid().get(
                client__email=data["email"],
                secret=data["password"]  # In this case, the password is the secret
            ).delete()
        except MagicLink.DoesNotExist as _:
            raise ValidationError("Invalid link.")

    def validate(self, attrs: Any) -> Any:
        method = attrs["method"]
        if method == "password":
            self._validate_password(attrs)
        elif method == "email_from_magic_link":
            self._validate_email_from_magic_link(attrs)
        else:
            raise ValidationError("Invalid Request", code=400)
        return attrs
