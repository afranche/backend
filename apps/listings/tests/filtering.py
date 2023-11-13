import base64
import os
import warnings
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from apps.listings.models import Category, Characteristic, ImageModel, Listing, Product, Variant


absolute_path = os.path.abspath("./apps/listings/tests/images/category_hero.png")


class CategoryFilterAPIViewTests(APITestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name='Category 1', description='Desc 1', language='eng', parent=None)
        self.category2 = Category.objects.create(name='Category 2', description='Desc 2', language='fra', parent=self.category1)
        
    def test_category_filtering(self):
        url = reverse('category-filter-api')
        
        # Test filtering by name
        response = self.client.get(url, {'name': 'Category 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Category 1')
        
        # Test filtering by language
        response = self.client.get(url, {'language': 'eng'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Category 1')
        
        # Test filtering by parent
        response = self.client.get(url, {'parent': 'null'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Category 1')
        
        # Test filtering by description
        response = self.client.get(url, {'description': 'Desc 2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Category 2')

class ListingFilterAPIViewTests(APITestCase):
    def get_image(self):
        with open(absolute_path, 'rb') as image:
            image_data = image.read()
        return base64.encodebytes(image_data).decode('utf-8')

    def setUp(self):
        # Create some listings
        product1 = Product.objects.create(name='Test Product', manufacturer='Manufacturer 1', price=10.0)
        product2 = Product.objects.create(name='Test Product 2', manufacturer='Manufacturer 2', price=20.0)
        self.category1 = Category.objects.create(name='Test Category Super')


        self.color_variant = Variant.objects.create(name='Blue')
        self.color_variant.images.add(ImageModel.objects.create(image=absolute_path))
        self.color_variant.save()
        characteristic_1 = Characteristic.objects.create(label="Colors", type="choices")
        characteristic_1.choices.add(self.color_variant)
        characteristic_1.save()
        self.listing1 = Listing.objects.create(product=product1, additional_price=10.0)
        self.listing1.characteristics.add(characteristic_1)
        self.listing1.categories.add(self.category1)
        self.listing1.save()
        self.listing2 = Listing.objects.create(product=product2, additional_price=15.0)
        self.absolute_path = os.path.abspath("./apps/listings/tests/images/category_hero.png")

        
    def test_listing_filtering(self):
        url = reverse('listing-filter-api')
        
        # Test filtering by additional price
        response = self.client.get(url, {'price': 10.0})
        warnings.warn(f'Warning: {response.data}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]["variants"][0]['price'], 10.0)
        
        # Test filtering by category
        response = self.client.get(url, {'category_name': 'Test Categ'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Test filtering by product name
        response = self.client.get(url, {'name': 'Test Produ'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
