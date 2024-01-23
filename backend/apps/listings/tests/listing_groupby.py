from rest_framework import status
from apps.listings.models import Listing

from apps.listings.tests.utils import BaseTestCase

class ListingGroupByTests(BaseTestCase):

    url = "/listings/product/"

    def test_get_valid_case(self):
        self.client.force_authenticate(user=self.admin_user)
        self.create_legit_listing()

        response = self.client.get(
            f'{self.url}?group_by=characteristics__label&page=1&page_size=10',
        format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        """
            Returning data formatted like this:
            [
                {
                    "id": 1,
                    "price": 12.0,
                    "name": "Product Name",
                    "description": "Product Description",
                    "default_image": { "id": 1, "image": "http://localhost:8000/media/..."},
                    "manufacturer": "L'Oréal",
                    "variants":
                        {
                            "Color": [
                                {
                                    "id": 1,
                                    "label": "Color",
                                    "value": "Red",
                                    "images": [
                                        {
                                            "id": 1,
                                            "image": "http://localhost:8000/media/..."
                                        }
                                    ],
                                    "additional_price": 0.0,
                                    "stock": 0,
                                    "is_available": false
                                },
                                {
                                    "id": 2,
                                    "label": "Color",
                                    "value": "Blue",
                                    "images": [
                                        {
                                            "id": 2,
                                            "image": "http://localhost:8000/media/..."
                                        }
                                    ],
                                    "additional_price": 0.0,
                                    "stock": 0,
                                    "is_available": false
                                }
                            ]
                        }   
                    ]
                }
            ]
        """
      
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(len(response.data['results'][0]['variants']), 2)
        self.assertEqual(len(response.data['results'][0]['variants']['Color']), 2)
        self.assertEqual(len(response.data['results'][0]['variants']['Size']), 2)
        self.assertEqual(response.data['results'][0]['variants']['Color'][0]['characteristics'],
                         {
                                "label": "Color",
                                "value": "Blue"
                         })
        self.assertEqual(response.data['results'][0]['variants']['Color'][1]['characteristics'],
                         {
                                "label": "Color",
                                "value": "Red"
                         })
        self.assertEqual(response.data['results'][0]['variants']['Size'][0]['characteristics'],
                         {
                                "label": "Size",
                                "value": "Large"
                         })
        self.assertEqual(response.data['results'][0]['variants']['Size'][1]['characteristics'],
                         {
                                "label": "Size",
                                "value": "Small"
                         })

    def test_create_listing(self):
        data = {
                    "id": 1,
                    "price": 12.0,
                    "name": "Product Name",
                    "description": "Product Description",
                    "categories": [],
                    "variants":
                        {
                            "Color": [
                                {
                                    "id": 1,
                                    "label": "Color",
                                    "value": "Red",
                                    "images": [
                                        {
                                            "image": self.get_image()
                                        }
                                    ],
                                    "additional_price": 0.0,
                                    "stock": 0,
                                },
                                {
                                    "id": 2,
                                    "label": "Color",
                                    "value": "Blue",
                                    "images": [
                                        {
                                            "image": self.get_image()
                                        }
                                    ],
                                    "additional_price": 0.0,
                                    "stock": 0,
                                }
                            ]
                        }   
                }
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            f'{self.url}?group_by=characteristics__label', data,
        format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Listing.objects.filter(name="Product Name").first()
        self.assertEqual(created.name, "Product Name")
        self.assertEqual(created.description, "Product Description")
        self.assertEqual(created.price, 12.0)

        self.assertEqual(created.products.count(), 2)
        self.assertTrue(created.products.first().characteristics['value'] in ["Red", "Blue"])
        self.assertTrue(created.products.last().characteristics['value'] in ["Red", "Blue"])
       