from rest_framework import status
from django.urls import reverse

from apps.listings.tests.utils import BaseTestCase

class ListingFilteringTests(BaseTestCase):
    url = "/listings/product/"

    def test_filter_by_price(self):
        self.create_legit_listing()
        filters = {'price': 10.0}
        response = self.client.get(self.url, filters, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(response.data['count'], 1)  # Expecting only one listing with price 10.0

    def test_filter_by_category_name(self):
        self.create_legit_listing()
        filters = {'category_name': 'Category 1'}
        response = self.client.get(self.url, filters, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(response.data['count'], 1)  # Expecting only one listing in 'Category 1'

    def test_filter_by_name(self):
        self.create_legit_listing()
        filters = {'name': 'Test list'}
        response = self.client.get(self.url, filters, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(response.data['count'], 1)  # Expecting only one listing with the specified name

    def test_filter_by_manufacturer(self):
        self.create_legit_listing()
        filters = {'manufacturer': 'Sample Manu'}
        response = self.client.get(self.url, filters, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_invalid_price(self):
        filters = {'price': 'invalid_price'}  # Invalid data type for price
        response = self.client.get(self.url, filters, format='json')
        self.assertEqual(response.data['count'], 0)
        # Add assertions for the response content if needed

    def test_filter_by_invalid_category_name(self):
        filters = {'category_name': 123}  # Invalid data type for category_name
        response = self.client.get(self.url, filters, format='json')
        self.assertEqual(response.data['count'], 0)
        # Add assertions for the response content if needed

    def test_filter_by_invalid_name(self):
        filters = {'name': {'invalid': 'data'}}  # Invalid data type for name
        response = self.client.get(self.url, filters, format='json')
        self.assertEqual(response.data['count'], 0)