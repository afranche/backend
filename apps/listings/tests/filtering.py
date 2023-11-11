import warnings
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from apps.listings.models import Category, Listing, Product

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
    def setUp(self):
        self.category = Category.objects.create(name='Test Category', language='eng')
        self.product = Product.objects.create(name='Test Product', manufacturer='Test Manufacturer', price=10.0)
        self.listing1 = Listing.objects.create(product=self.product, additional_price=5.0)
        self.listing1.categories.add(self.category)
        self.listing2 = Listing.objects.create(product=Product.objects.create(name='Test Product 2', price=44), additional_price=7.0)
        self.listing2.categories.add(self.category)
        
    def test_listing_filtering(self):
        url = reverse('listing-filter-api')
        
        # Test filtering by additional price
        response = self.client.get(url, {'price': 10.0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['price'], 10.0)
        
        # Test filtering by category
        response = self.client.get(url, {'category_name': 'Test Categ'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Test filtering by product name
        response = self.client.get(url, {'name': 'Test Produ'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
