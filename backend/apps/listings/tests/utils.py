import base64
import os
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.listings.models import Category, ImageModel, Listing, Manufacturer, Product
from apps.users.models import Client

absolute_path = os.path.abspath("./apps/listings/tests/images/category_hero.png")
if absolute_path and not absolute_path.startswith('/'):
    absolute_path = '/' + absolute_path


class BaseTestCase(APITestCase):
    def setUp(self):

        # Create a sample manufacturer for testing
        self.manufacturer = Manufacturer.objects.create(
            name='Sample Manufacturer',
            phone_number='123-456-7890',
            description='Sample description'
        )
        self.client_user = Client.objects.create_user(email='client@outlook.pl', password='client_password')
        self.admin_user = Client.objects.create_superuser(email='admin@palestinement.pl', password='admin_password')
        self.absolute_path = os.path.abspath("./apps/listings/tests/images/category_hero.png")
        self.product1 = Product.objects.create(
            is_available=True,
            is_active=True,
            characteristics={"label": "color", "value": "red"},
            is_customized=False,
            is_sold=False,
            additional_price=5.0
        )

        self.product2 = Product.objects.create(
            is_available=True,
            is_active=True,
            characteristics={"label": "size", "value": "XL"},
            is_customized=True,
            is_sold=False,
            additional_price=10.0
        )
        self.sold_product = Product.objects.create(
            is_available=True,
            is_active=True,
            characteristics={"label": "size", "value": "XL"},
            is_customized=True,
            is_sold=True,
            additional_price=10.0
        )
        image = ImageModel.objects.create(image=self.absolute_path)
        for p in [self.product1, self.product2, self.sold_product]:
            p.images.add(image)
            p.save()
        self.category1 = Category.objects.create(name='Category 1', description='Desc 1', language='eng', parent=None)
        self.category2 = Category.objects.create(name='Category 2', description='Desc 2', language='fra', parent=self.category1)

    def create_legit_listing(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "Test Listing",
            "manufacturer": self.manufacturer.id,
            "categories": [self.category1.id],
            "price": 10.0,
            "options": [
                        {"label": "Color", "value": "Red", "stock": 2},
                        {"label": "Color","value": "Blue", "stock": 3},
                        {"label": "Size", "value": "Small", "stock": 1},
                        {"label": "Size", "value": "Large", "stock": 4},
                    ]
        }
        return self.client.post('/listings/product/', data, format='json')

    def create_listing_sold_products(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "Test Listing",
            "manufacturer": self.manufacturer.id,
            "categories": [self.category1.id],
            "price": 10.0,
            "options": [
                        {"label": "genre", "value": "femme", "stock": 2, "is_sold": True},
                        {"label": "genre", "value": "homme", "stock": 3, "is_sold": True},
                    ]
        }
        return self.client.post('/listings/product/', data, format='json')

    def tearDown(self) -> None:
        self.client_user.delete()
        self.admin_user.delete()
        Listing.objects.all().delete()
        Product.objects.all().delete()
        return super().tearDown()

    def get_image(self):
        with open(self.absolute_path, 'rb') as image:
            image_data = image.read()
        return base64.encodebytes(image_data).decode('utf-8')
