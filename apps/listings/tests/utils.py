import base64
import os
from rest_framework.test import APITestCase

from apps.listings.models import Category, Characteristic, ImageModel, Listing, Product, Variant
from apps.users.models import Client

absolute_path = os.path.abspath("./apps/listings/tests/images/category_hero.png")
if absolute_path and not absolute_path.startswith('/'):
    absolute_path = '/' + absolute_path


class BaseTestCase(APITestCase):
    def setUp(self):
        self.client_user = Client.objects.create_user(email='client@outlook.pl', password='client_password')
        self.admin_user = Client.objects.create_superuser(email='admin@palestinement.pl', password='admin_password')
        self.absolute_path = os.path.abspath("./apps/listings/tests/images/category_hero.png")
        product1 = Product.objects.create(name='Product 1', manufacturer='Manufacturer 1', price=10.0)
        product2 = Product.objects.create(name='Product 2', manufacturer='Manufacturer 2', price=20.0)
        self.category1 = Category.objects.create(name='Category 1', description='Desc 1', language='eng', parent=None)
        self.category2 = Category.objects.create(name='Category 2', description='Desc 2', language='fra', parent=self.category1)

        self.color_variant = Variant.objects.create(attr_name='Blue')
        self.color_variant.images.add(ImageModel.objects.create(image=self.absolute_path))
        self.color_variant.save()
        characteristic_1 = Characteristic.objects.create(label="Colors", type="choices")
        characteristic_1.choices.add(self.color_variant)
        characteristic_1.save()
        self.listing1 = Listing.objects.create(product=product1, additional_price=10.0)
        self.listing1.characteristics.add(characteristic_1)
        self.listing1.categories.add(self.category1)
        self.listing1.save()
        self.listing2 = Listing.objects.create(product=product2, additional_price=15.0)
        self.listing2.categories.add(self.category2)

    def tearDown(self) -> None:
        self.client_user.delete()
        self.admin_user.delete()
        Listing.objects.all().delete()
        Product.objects.all().delete()
        Characteristic.objects.all().delete()
        return super().tearDown()

    def get_image(self):
        with open(self.absolute_path, 'rb') as image:
            image_data = image.read()
        return base64.encodebytes(image_data).decode('utf-8')
