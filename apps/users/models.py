# TODO: Add type-stubs afterwards for pycountry
import pycountry  # type: ignore
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
