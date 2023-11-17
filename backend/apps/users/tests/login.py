from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.users.models import Client, MagicLink
from apps.users.serializers import LoginSerializer

class TestModels(TestCase):
    def setUp(self):
        self.client = Client.objects.create_user(email="test@example.com", )

    def test_magic_link_expiration(self):
        magic_link = MagicLink.objects.create(client=self.client)
        expired_magic_link = MagicLink.objects.create(
            client=self.client,
            secret='secret', 
            expires_at=timezone.now() - timezone.timedelta(minutes=60)  # Creating an expired link
        )
        
        self.assertIn(magic_link, MagicLink.objects.from_valid())
        self.assertNotIn(expired_magic_link, MagicLink.objects.from_valid())
        self.assertIn(expired_magic_link, MagicLink.objects.from_expired())

    def test_magic_link_invalid(self):
        with self.assertRaises(MagicLink.DoesNotExist):
            MagicLink.objects.from_valid().get(
                client=self.client,
                secret="invalid_secret"
            )


class TestSerializers(TestCase):
    def setUp(self):
        self.client = Client.objects.create_user(email="test@example.com", password="test_password")

    def test_login_serializer_with_invalid_password(self):
        data = {
            "method": "password",
            "email": "test@example.com",
            "password": "wrong_password"
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_valid_login_with_email_password(self):
        data = {
            "method": "password",
            "email": "test@example.com",
            "password": "test_password"
        }
        print("client password:", self.client.password)
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_login_serializer_with_valid_magic_link(self):
        magic_link = MagicLink.objects.create(client=self.client, secret="lol")
        data = {
            "method": "email_from_magic_link",
            "email": "test@example.com",
            "password": magic_link.secret
        }
        serializer = LoginSerializer(data=data)
        print(serializer.is_valid())
        print(serializer.errors)
        self.assertTrue(serializer.is_valid())

    # Extend with more tests to cover other scenarios within the LoginSerializer