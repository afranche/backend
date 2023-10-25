from __future__ import annotations

import datetime

# TODO: Add type-stubs afterwards for pycountry
import pycountry  # type: ignore
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.management.utils import get_random_secret_key
from django.db import models
from django.utils.translation import gettext as _


class Address(models.Model):
    # TOFIX: unable to create a country in french
    COUNTRY_CHOICES = tuple((country.alpha_3, _(country.name)) for country in pycountry.countries)  # type: ignore

    timestamp = models.DateTimeField(
        _("Address creation timestamp"),
        help_text=""" The timestamp for an address needs to be kept to comply with
                      local privacy laws like GDPR. We might issue notices and proceed
                      to automatically delete the address once the legal period requires
                      us to do so. """,
        auto_now_add=True,
    )
    name = models.CharField(
        _("Name"),
        max_length=128,
    )
    address1 = models.CharField(
        _("Address line 1"),
        max_length=128,
    )
    address2 = models.CharField(
        _("Address line 2"),
        max_length=128,
    )
    zip_code = models.CharField(
        _("ZIP / Postal code"),
        max_length=5,
    )
    region = models.CharField(
        _("Region"),
        max_length=128,
    )
    city = models.CharField(
        _("City"),
        max_length=128,
    )
    country = models.CharField(  # type: ignore
        _("Country"), max_length=3, choices=COUNTRY_CHOICES  # type: ignore
    )


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        # Create and save a superuser with the given email and password.
        user = self.create_user(
            email,
            password=password,
            **extra_fields,
        )
        user.is_staff = True
        # user.is_admin = True
        user.save(using=self._db)
        return user


class Client(PermissionsMixin, AbstractBaseUser):
    """
    We keep a specific class to pair e-mails to a specific client. This way
    we can refer to the user through the `request.user` variable and prevent
    having him logging in using a password, etc..
    """

    USERNAME_FIELD = "email"

    email = models.EmailField(_("email address"), unique=True)
    password = models.CharField(_("password"), max_length=128, blank=True, null=True)
    address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, blank=True, null=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    @property
    def is_admin(self):
        return self.is_staff
    
    @property
    def is_superuser(self):
        return self.is_staff
    
    @property
    def is_active(self):
        return True

class MagicLinkQuerySet(models.QuerySet["MagicLink"]):
    def from_valid(self) -> MagicLinkQuerySet:
        return self.filter(expires_at__gt=datetime.datetime.now())

    def from_expired(self):
        return self.filter(expires_at__lte=datetime.datetime.now())


class MagicLink(models.Model):
    """ """

    @staticmethod
    def _get_expiration_date():
        return str(datetime.datetime.now() + datetime.timedelta(minutes=30))

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name=_("client")
    )
    secret = models.CharField(
        _("Secret"), default=get_random_secret_key, auto_created=True, max_length=50
    )
    expires_at = models.DateTimeField(default=_get_expiration_date())  # should be called otherwise it is unserializable by Django
    objects = MagicLinkQuerySet.as_manager()
