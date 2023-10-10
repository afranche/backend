from django.db import models
from django.utils.translation import gettext as _
from django.utils.text import slugify

import pycountry
    
LANGUAGE_CHOICES = ((language.alpha_3, _(language.name)) for language in pycountry.languages)  # type: ignore

class Characteristic(models.Model):
    """
        Characteristic is a property used to customize a product.
        Ex: select between 3 colors, input a text that will appear on the product, etc.
    """

    class CharacteristicType(models.TextChoices):
        CHOICES = "choices", _("Choices")
        INPUT = "input", _("Input")

    choices = models.JSONField(_("Characteristic choices"), default=[], blank=True)
    input = models.CharField(_("Characteristic input"), max_length=64, default="", blank=True)
    type = models.CharField(
        _("Characteristic Type"),
        choices=CharacteristicType.choices,
        max_length=64,
        blank=False,
    )
    multiple_choices = models.BooleanField(_("Multiple choices"), default=False)


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

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Product")
    )
    lang = models.CharField(  # type: ignore
        _("Language"), max_length=3, choices=LANGUAGE_CHOICES  # type: ignore
    )
    name = models.CharField(_("Product Name"), max_length=64)
    description = models.TextField(_("Product Description"), blank=True, default="")
    characteristics = models.ManyToManyField(Characteristic, verbose_name=_("Characteristics"))


class Listing(models.Model):
    additional_price = models.FloatField(_("Additional price for that listing"))
    characteristics = models.JSONField(_("Listing characteristics"))


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=100, allow_unicode=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children')
    listings = models.ManyToManyField(Product, related_name='categories') # Should haveI put Listing Model instead ?
    language = models.CharField(_("Language"), max_length=3, choices=LANGUAGE_CHOICES, default='fr')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f'<Category {self.name.lower()}, {self.listings.object.count()} listings>'

    def save(self, *args, **kwargs):
        # Automatically generate the slug from the category name
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)