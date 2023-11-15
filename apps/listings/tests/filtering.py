import warnings
from django.urls import reverse
from rest_framework import status
from apps.listings.models import ImageModel, Variant

from apps.listings.tests.utils import BaseTestCase



class CategoryFilterAPIViewTests(BaseTestCase):
        
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

class ListingFilterAPIViewTests(BaseTestCase):
        
    def test_listing_filtering(self):
        url = reverse('listing-filter-api')
        
        # Test filtering by additional price
        response = self.client.get(url, {'price': 10.0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        warnings.warn(f"Response data: {response.data}")
        result = response.data['results'][0]
        self.assertEqual(result['id'], self.listing1.id)
        self.assertEqual(result['name'], 'Product 1')
        self.assertEqual(result['manufacturer'], 'Manufacturer 1')
        self.assertEqual(result['price'], 10.0)
        self.assertEqual(result['default_image']['id'], ImageModel.objects.first().id)
        # self.assertEqual(result['default_image']['image'], ImageModel.objects.first().image.url)
        self.assertEqual(result['category']['id'], self.category1.id)
        self.assertEqual(result['category']['name'], 'Category 1')
        self.assertEqual(result['variants'][0]['label'], 'Colors')
        self.assertEqual(result['variants'][0]['choices'][0]['id'], self.color_variant.id)
        self.assertEqual(result['variants'][0]['choices'][0]['attr_name'], 'Blue')
        self.assertEqual(result['variants'][0]['choices'][0]['additional_price'], (0.0,))
        self.assertEqual(result['variants'][0]['choices'][0]['stock'], 0)
        self.assertEqual(result['variants'][0]['choices'][0]['is_available'], True)
        self.assertEqual(result['variants'][0]['choices'][0]['images'][0]['id'], ImageModel.objects.first().id)
        
        '''
        self.assertEqual(response.data['results'][0], {
            "id": self.listing1.id,
            "name": "Product 1",
            "manufacturer": "Manufacturer 1",
            "price": 10.0,
            "default_image": {
                "id": ImageModel.objects.first().id,
                "image": ImageModel.objects.first().image.url,
            },
            "category": {
                "id": self.category1.id,
                "name": "Category 1",
            },
            "variants": [
                {
                    "label": "Colors",
                    "choices": [
                        {
                            "id": self.color_variant.id,
                            "attr_name": "Blue",
                            "additional_price": 0,
                            "stock": 0,
                            "is_available": True,
                            "images": [
                                {
                                    "id": ImageModel.objects.first().id,
                                    "image": ImageModel.objects.first().image.url,
                                }
                            ]
                        }

                    ]
                }
            ]
        })'''
        
        # Test filtering by category
        response = self.client.get(url, {'category_name': 'Categ'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Test filtering by product name
        response = self.client.get(url, {'name': 'Produ'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
