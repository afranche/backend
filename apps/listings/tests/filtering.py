import warnings
from django.urls import reverse
from rest_framework import status

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
        self.assertEqual(response.data['results'][0]["variants"][0]['price'], 10.0)
        
        # Test filtering by category
        response = self.client.get(url, {'category_name': 'Categ'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Test filtering by product name
        response = self.client.get(url, {'name': 'Produ'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
