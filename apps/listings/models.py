from django.db import models
from django.utils.translation import gettext as _

import pycountry


class Product(models.Model):
    class ProductType(models.IntegerChoices):
        OTHER = 0
        FOOD = 1

    type = models.IntegerField(
        _("Product Type"), choices=ProductType.choices, default=ProductType.OTHER
    )
    manufacturer = models.CharField(_("Manufacturer"), max_length=64)
    price = models.FloatField(_("Price"))


class ProductPresentation(models.Model):
    LANGUAGE_CHOICES = ((language.alpha_2, _(language.name)) for language in pycountry.languages)  # type: ignore

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Product")
    )
    lang = models.CharField(  # type: ignore
        _("Language"), max_length=3, choices=COUNTRY_CHOICES  # type: ignore
    )
    name = models.CharField(_("Product Name"), max_length=64)
    description = models.TextField(_("Product Description"), blank=True, default="")
    characteristics = models.JSONField(_("Product characteristics"))


class Listing(models.Model):
    additional_price = models.FloatField(_("Additional price for that listing"))
    characteristics = models.JSONField(_("Listing characteristics"))
