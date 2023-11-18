import warnings
from django.urls import reverse
from rest_framework import status
from apps.listings.models import Listing

from apps.listings.tests.utils import BaseTestCase

class ListingCreationTests(BaseTestCase):

    url = "/listings/product/"

    def test_create_valid_case(self):
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

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test category
        self.assertEqual(response.data['categories'][0]['id'], self.category1.id)

        # test manufacturer
        self.assertEqual(response.data['manufacturer'], self.manufacturer.id)

        # test data representation is flatten
        self.assertEqual(len(response.data['products']), 4)
        # check if the characteristics are correct
        for product in response.data['products']:
            if product['characteristics']['label'] == 'Color':
                self.assertIn(product['characteristics']['value'], ['Red', 'Blue'])
            elif product['characteristics']['label'] == 'Size':
                self.assertIn(product['characteristics']['value'], ['Small', 'Large'])
            else:
                self.fail("Unexpected characteristics")
        # test data is saved in database
        listing = Listing.objects.get(name="Test Listing")
        # test categories in db
        self.assertEqual(listing.categories.count(), 1)
        # test stock is the total, so 10
        self.assertEqual(listing.products.count(), 10)


    def test_create_unauthenticated(self):
        self.client.force_authenticate(self.client_user)
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

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_listing_with_images(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "Test Listing",
            "manufacturer": self.manufacturer.id,
            "categories": [self.category1.id],
            "price": 10.0,
            "options": [
                        {"label": "Color", "value": "Red", "stock": 2, "images": [{"image": self.get_image()}]},
                        {"label": "Color","value": "Blue", "stock": 3, "images": [{"image": self.get_image()}]},
                        {"label": "Size", "value": "Small", "stock": 1, "images": [{"image": self.get_image()}]},
                        {"label": "Size", "value": "Large", "stock": 4, "images": [{"image": self.get_image()}]},
                    ]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test category
        self.assertEqual(response.data['categories'][0]['id'], self.category1.id)

        # test images
        self.assertEqual(len(response.data['products'][0]['images']), 1)
        self.assertEqual(response.data['products'][0]['images'][0]['image'].startswith('https://'), True)
        self.assertEqual(len(response.data['products'][1]['images']), 1)
        self.assertEqual(response.data['products'][1]['images'][0]['image'].startswith('https://'), True)
