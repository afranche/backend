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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("First Name"), max_length=112, blank=True, null=True)
    phone_number = models.CharField(_("Phone Number"), max_length=112, blank=True, null=True)
    # TODO: GeoJson location coordinates
    # location = models.PointField(_("Location"), blank=True, null=True)
    pictures = models.ManyToManyField(ImageModel, verbose_name=_("Manufacturer Pictures"), blank=True)
    description = models.TextField(_("Manufacturer Description"), blank=True, default=str)

    
    @property
    def default_picture(self):
        return self.pictures.first()
    
    def __str__(self):
        return f'{self.name} - {self.phone_number}'

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_available = models.BooleanField(_("Is available"), default=True)
    is_active = models.BooleanField(_("Is active"), default=True)
    # {"label": "color", "value": "red"} 
    # or {"label": "size", "value": "XL"}
    # or for customized ones {"label": "custom", "value": "custom"} <- will be set by the client during order creation
    characteristics = models.JSONField(_("Product Characteristics"), blank=True, null=True)
    images = models.ManyToManyField(ImageModel, verbose_name=_("Product Pictures"), blank=True)
    orders = models.ForeignKey("orders.Order", verbose_name=_("Orders"), blank=True, related_name='products', null=True, on_delete=models.SET_NULL)
    is_customised = models.BooleanField(_("Is customised"), default=False)
    is_sold = models.BooleanField(_("Is sold"), default=False)
    sold_at = models.DateTimeField(_("Sold at"), blank=True, null=True)
    description = models.TextField(_("Variation Description"), blank=True, default=str)
    additional_price = models.FloatField(_("Additional price for that variant"), default=0.0)
    listing = models.ForeignKey("Listing", verbose_name=_("Listing"), blank=True, related_name='products', null=True, on_delete=models.SET_NULL)

    def delete(self, *args, **kwargs):
        if self.is_sold:
            self.is_active = False
            self.images.all().delete()
            return self.save()
        else:
            return super().delete(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.characteristics.get("label", "No label")} : {self.characteristics.get("value", "No value")}'

class Listing(models.Model):
    class ProductType(models.IntegerChoices):
        OTHER = 0
        FOOD = 1
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    categories = models.ManyToManyField(Category, verbose_name=_("Listing Categories"), blank=True)
    type = models.IntegerField(
        _("Product Type"), choices=ProductType.choices, default=ProductType.OTHER
    )
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name=_("Manufacturer"), blank=True, null=True, default=None)
    price = models.FloatField(_("Price"), default=0)
    weight = models.FloatField(_("Weight in g"), blank=True, null=True, default=25)
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
    def stock(self):
        return self.products.orders.filter(is_sold=False).count()

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.description = self.description.strip()
        return super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        self.is_active = False
        for product in self.products.all():
            product.delete()
        self.save()

