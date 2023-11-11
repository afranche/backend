from collections.abc import Iterable
from uuid import uuid4
from django.db import models
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField
import base64
from django.core.files.base import ContentFile

import pycountry
    
LANGUAGE_CHOICES = ((language.alpha_3, _(language.name)) for language in pycountry.languages)  # type: ignore

class Category(models.Model):
    name = models.CharField(blank=True, null=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.FileField(upload_to='categories_cover/', blank=True, null=True, max_length=512)
    slug = models.SlugField(blank=True, null=True, unique=True, max_length=100, allow_unicode=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    language = models.CharField(_("Language"), max_length=3, choices=LANGUAGE_CHOICES, default='fra')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Automatically generate the slug from the category name
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Characteristic(models.Model):
    """
        Characteristic is a property used to customize a product.
        Ex: select between 3 colors, input a text that will appear on the product, etc.
    """

    class CharacteristicType(models.TextChoices):
        CHOICES = "choices", _("Choices")
        INPUT = "input", _("Input")

    choices = ArrayField(models.CharField(_("Characteristic choices"), max_length=112), blank=True, default=list)
    # input = models.CharField(_("Characteristic input"), max_length=64, default="", blank=True)
    #  this is the user's choice so it should be on order apps model not here
    label = models.CharField(_("Characteristic label"), max_length=100, blank=False, default="")
    type = models.CharField(
        _("Characteristic Type"),
        choices=CharacteristicType.choices,
        max_length=112,
        blank=False,
    )
    multiple_choices = models.BooleanField(_("Multiple choices"), default=False)

    def save(self, *args, **kwargs) -> None:
        if self.type == Characteristic.CharacteristicType.INPUT:
            self.choices = []
        else:
            self.choices = [choice.strip() for choice in self.choices if choice.strip() != ""]
        return super().save(*args, **kwargs)


class Image(models.Model):
    image = models.FileField(upload_to='products_images/', blank=True, null=True)


class Product(models.Model):
    class ProductType(models.IntegerChoices):
        OTHER = 0
        FOOD = 1

    type = models.IntegerField(
        _("Product Type"), choices=ProductType.choices, default=ProductType.OTHER
    )
    manufacturer = models.CharField(_("Manufacturer"), max_length=112)
    images = models.ManyToManyField(Image, verbose_name=_("Product Images"), default=None, blank=True)
    stock = models.IntegerField(_("Stock"), default=0)
    is_available = models.BooleanField(_("Is available"), default=True)
    price = models.FloatField(_("Price"))
    weight = models.FloatField(_("Weight in g"), blank=True, null=True, default=25)
    conservation = models.CharField(_("Conservation"), max_length=124, blank=True)
    lang = models.CharField(  # type: ignore
        _("Language"), max_length=3, choices=LANGUAGE_CHOICES, default='fra'  # type: ignore
    )
    name = models.CharField(_("Product Name"), max_length=112)
    description = models.TextField(_("Product Description"), blank=True, default=str)

    def __str__(self):
        return f'{self.name} - {self.manufacturer} - {self.price}€, id: {self.id}'

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.manufacturer = self.manufacturer.strip()
        self.description = self.description.strip()
        return super().save(*args, **kwargs)


class Listing(models.Model):

    characteristics = models.ManyToManyField(Characteristic, verbose_name=_("Listing Characteristics"))
    additional_price = models.FloatField(_("Additional price for that listing"), default=0.0)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Product")
    )
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return f'{self.product} - Category: {self.categories} - Characteristics: {self.characteristics}'


