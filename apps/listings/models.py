from django.db import models
from django.utils.translation import gettext as _
from django.utils.text import slugify

import pycountry

from settings.settings import CATEGORY_FOLDER_NAME, PRODUCT_FOLDER_NAME

def base64_image_to_file (image) :
    from django.core.files.base import ContentFile
    import base64

    if isinstance(image, ContentFile):
        if image.name is None:
            image.name = get_filename(image.file.read())
        return image
    if 'data:' in image and ';base64,' in image :
            header, image = image.split(';base64,')
    decoded_image = base64.b64decode(image)
    data = ContentFile(decoded_image, name=get_filename(decoded_image))
    return data

def get_filename(decoded_image):
    import uuid
    filename = str(uuid.uuid4())[:12]
    extension = get_file_extension(filename, decoded_image)

    return f"{filename}.{extension}"

def get_file_extension (file_name, decoded_image) :
    import imghdr

    extension = imghdr.what(file_name, decoded_image)
    extension = "jpg" if extension == "jpeg" else extension

    return extension
    
LANGUAGE_CHOICES = ((language.alpha_3, _(language.name)) for language in pycountry.languages)  # type: ignore

class Category(models.Model):
    name = models.CharField(blank=True, null=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=CATEGORY_FOLDER_NAME, blank=True, null=True, max_length=512)
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


class ImageModel(models.Model):
    image = models.ImageField(upload_to=PRODUCT_FOLDER_NAME, blank=True, null=True, max_length=512)
    variant = models.ForeignKey('Variant', on_delete=models.CASCADE, blank=True, null=True, related_name='images')


class Variant(models.Model):
    stock = models.IntegerField(_("Stock"), default=0)
    is_available = models.BooleanField(_("Is available"), default=True)
    # variation name can be "size", "color", "material", "gender" etc.
    name = models.CharField(_("Variation Name"), max_length=112)
    description = models.TextField(_("Variation Description"), blank=True, default=str)


class Characteristic(models.Model):
    """
        Characteristic is a property used to customize a product.
        Ex: select between 3 colors, input a text that will appear on the product, etc.
    """

    class CharacteristicType(models.TextChoices):
        CHOICES = "choices", _("Choices")
        INPUT = "input", _("Input")

    choices = models.ManyToManyField(Variant, verbose_name=_("Characteristic choices"), blank=True)
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

    def __str__(self):
        return f'{self.label} - ({self.type})'


class Product(models.Model):
    class ProductType(models.IntegerChoices):
        OTHER = 0
        FOOD = 1

    type = models.IntegerField(
        _("Product Type"), choices=ProductType.choices, default=ProductType.OTHER
    )
    manufacturer = models.CharField(_("Manufacturer"), max_length=112)
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

    characteristics = models.ManyToManyField(Characteristic, verbose_name=_("Listing Characteristics"), blank=True)
    additional_price = models.FloatField(_("Additional price for that listing"), default=0.0)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Product")
    )
    categories = models.ManyToManyField(Category, verbose_name=_("Listing Categories"), blank=True)

    def __str__(self):
        return f'{self.product} - Category: {self.categories} - Characteristics: {self.characteristics}'
