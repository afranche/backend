import warnings
from rest_framework import status
from apps.listings.models import Listing

from apps.listings.tests.utils import BaseTestCase

class ListingUpdateTests(BaseTestCase):
    url = "/listings/product"
    def test_update_listing_name(self):
        response = self.create_legit_listing()

        data = {
            "name": "Updated Listing Name",
        }
        upd_url = f'{self.url}/{response.data["id"]}/'
        response = self.client.put(upd_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_listing = Listing.objects.get(id=response.data['id'])
        self.assertEqual(updated_listing.name, "Updated Listing Name")

    def test_update_listing_with_new_options(self):
        self.create_legit_listing()
        response = self.create_legit_listing()
        data = {
            "options": [
                        {"label": "size", "value": "Medium", "stock": 2},
                        {"label": "size",  "value": "Large", "stock": 3},
                    ]
        }
        upd_url = f'{self.url}/{response.data["id"]}/'
        response = self.client.put(upd_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_listing = Listing.objects.get(id=response.data['id'])
        self.assertEqual(updated_listing.products.count(), 5)
        self.assertEqual(updated_listing.products.filter(characteristics__value="Medium").count(), 2)
        self.assertEqual(updated_listing.products.filter(characteristics__value="Large").count(), 3)

        # test reponse data structure is flatten
        self.assertEqual(len(response.data['products']), 2)

    def test_update_with_sold_products(self):

        response = self.create_listing_sold_products()
        data = {
            "options": [
                {"label": "genre", "value": "femme", "stock": 2},
                {"label": "genre", "value": "homme", "stock": 3},
            ],
        }
        upd_url = f'{self.url}/{response.data["id"]}/'

        response = self.client.put(upd_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_listing = Listing.objects.get(id=response.data['id'])
        # Originally self.listing2 has 3 products, so 5 more stock is added
        self.assertEqual(updated_listing.products.count(), 10)

        # test reponse data structure is flatten
        self.assertEqual(len(response.data['products']), 2)

    def test_update_listing_image(self):
        response = self.create_legit_listing()
        data = {
            "options": [
                        {"label": "Color", "value": "Red", "stock": 2, "images": []},
                        {"label": "Color","value": "Blue", "stock": 3, "images": []},
                        {"label": "Size", "value": "Small", "stock": 1, "images": []},
                        {"label": "Size", "value": "Large", "stock": 4, "images": []},
                    ]
        }
        upd_url = f'{self.url}/{response.data["id"]}/'
        response = self.client.put(upd_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test reponse data structure is flatten
        self.assertEqual(len(response.data['products']), 4)

        # test update images
        data = {
            "options": [
                        {"label": "Color", "value": "Red", "stock": 2, "images": [{"image": self.get_image()}]},
                        {"label": "Color","value": "Blue", "stock": 3, "images": [{"image": self.get_image()}]},
                        {"label": "Size", "value": "Small", "stock": 1, "images": [{"image": self.get_image()}]},
                        {"label": "Size", "value": "Large", "stock": 4, "images": [{"image": self.get_image()}]},
                    ]
        }
        response = self.client.put(upd_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test images are set
        self.assertEqual(len(response.data['products'][0]['images']), 1)
        self.assertEqual(len(response.data['products'][1]['images']), 1)
        self.assertEqual(len(response.data['products'][2]['images']), 1)
        self.assertEqual(len(response.data['products'][3]['images']), 1)


