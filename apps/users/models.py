from typing import Collection

# TODO: Add type-stubs afterwards for pycountry
import pycountry  # type: ignore
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _


class Address(models.Model):
    COUNTRY_CHOICES = ((country.alpha_3, _(country.name)) for country in pycountry.countries)  # type: ignore

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


class Client(PermissionsMixin, AbstractBaseUser):
    """
    We keep a specific class to pair e-mails to a specific client. This way
    we can refer to the user through the `request.user` variable and prevent
    having him logging in using a password, etc..
    """

    USERNAME_FIELD = "email"

    email = models.EmailField(_("email address"), primary_key=True)
    password = models.CharField(_("password"), max_length=128, blank=True, null=True)
    address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, blank=True, null=True
    )

    is_active = True

    objects = BaseUserManager

    def clean_fields(self, exclude: Collection[str] | None = ...) -> None:
        if self.is_superuser:
            raise ValidationError("Client are not allowed to be super-users.")

        return super().clean_fields(exclude)
