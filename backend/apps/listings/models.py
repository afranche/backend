from datetime import timezone
import uuid
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

class Manufacturer(models.Model):
    name = models.CharField(_("First Name"), max_length=112, blank=True, null=True)
    phone_number = models.CharField(_("Phone Number"), max_length=112, blank=True, null=True)
    # TODO: GeoJson location coordinates
    # location = models.PointField(_("Location"), blank=True, null=True)
    pictures = models.ManyToManyField(ImageModel, verbose_name=_("Manufacturer Pictures"), blank=True)
    description = models.TextField(_("Manufacturer Description"), blank=True, default=str)


    @property
    def default_picture(self):
        return self.pictures.first()  # type: ignore

    def __str__(self):
        return f'{self.name} - {self.phone_number}'

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    characteristics = models.JSONField(_("Product Characteristics"), blank=True, null=True)
    description = models.TextField(_("Variation Description"), blank=True, default=str)
    additional_price = models.FloatField(_("Additional price for that variant"), default=0.0)

    # {"label": "color", "value": "red"}
    # or {"label": "size", "value": "XL"}
    # or for customized ones {"label": "custom", "value": "custom"} <- will be set by the client during order creation
    is_customized = models.BooleanField(_("Is customized"), default=False)
    is_sold = models.BooleanField(_("Is sold"), default=False)
    sold_at = models.DateTimeField(_("Sold at"), blank=True, null=True)
    is_available = models.BooleanField(_("Is available"), default=True)
    is_active = models.BooleanField(_("Is active"), default=True)

    images = models.ManyToManyField(ImageModel, verbose_name=_("Product Pictures"), blank=True)
    in_order = models.ForeignKey("orders.Order", verbose_name=_("Orders"), blank=True, related_name='products', null=True, on_delete=models.SET_NULL)
    listing = models.ForeignKey("Listing", verbose_name=_("Listing"), blank=True, related_name='products', null=True, on_delete=models.SET_NULL)


    def delete(self, *args, **kwargs):
        if self.is_sold:
            self.is_active = False
            for i in self.images.all():  # type: ignore
                i.delete()
            return self.save()
        else:
            return super().delete(*args, **kwargs)

    def __str__(self) -> str:
        if self.characteristics is not None:
            return f'{self.characteristics.get("label", "No label")} {self.characteristics.get("value", "No value")}'
        return f'Product {self.id}, sold ? {self.is_sold}'


class Listing(models.Model):
    class ProductType(models.IntegerChoices):
        OTHER = 0
        FOOD = 1

    categories = models.ManyToManyField(Category, verbose_name=_("Listing Categories"), blank=True)
    type = models.IntegerField(
        _("Product Type"), choices=ProductType.choices, default=ProductType.OTHER  # type: ignore
    )
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name=_("Manufacturer"), blank=True, null=True, default=None)
    price = models.FloatField(_("Price"), default=0)  # type: ignore
    weight = models.FloatField(_("Weight in g"), blank=True, null=True, default=25)  # type: ignore
    conservation = models.CharField(_("Conservation"), max_length=124, blank=True)
    lang = models.CharField(  # type: ignore
        _("Language"), max_length=3, choices=LANGUAGE_CHOICES, default='fra'  # type: ignore
    )
    name = models.CharField(_("Product Name"), max_length=112, default="Unnamed Product")
    description = models.TextField(_("Product Description"), blank=True, default=str)
    is_active = models.BooleanField(_("Is active"), default=True)

    def __str__(self):
        return f'{self.name} - Category: {self.categories}'

    @property
    def default_image(self):
        product = self.products.filter(is_active=True, images__image__isnull=False).first()
        if product is None:
            return None
        return product.images.first()

    @property
    def stock(self):
        return self.products.orders.filter(is_sold=False).count()

    def save(self, *args, **kwargs):
        self.name = self.name.strip()  # type: ignore
        self.description = self.description.strip()  # type: ignore
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_active = False
        for product in self.products.all():  # type: ignore
            product.delete()
        self.save()


class Coupon(models.Model):
    code = models.CharField(_("Coupon Code"), max_length=20, unique=True, primary_key=True)
    discount = models.FloatField(_("Discount Amount"))
    active = models.BooleanField(_("Active"), default=True)
    expiration_date = models.DateTimeField(_("Expiration Date"), null=True, blank=True)

    def is_expired(self):
        # FIXME(adina): there is no now() in timezone class
        return self.expiration_date and self.expiration_date < timezone.now()

    is_expired.boolean = True  # Adding a boolean icon in the admin

    def __str__(self):
        return f"{self.code} - {self.discount}%"
