# tests.py
import warnings
from django.urls import reverse
from rest_framework import status
from apps.listings.models import Manufacturer

from apps.listings.serializers import ManufacturerSerializer
from apps.listings.tests.utils import BaseTestCase

class ManufacturerTests(BaseTestCase):
    url = '/listings/manufacturer'
    def test_manufacturer_creation(self):
        # Ensure that the manufacturer is created correctly
        self.assertEqual(Manufacturer.objects.count(), 1)

    def test_manufacturer_list_view(self):
        # Ensure that the manufacturer list view returns a 200 status code
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.url}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure that the correct number of manufacturers is returned in the response
        self.assertEqual(len(response.data), 1)

    def test_manufacturer_update_view(self):
        # Ensure that the manufacturer update view returns a 200 status code
        self.client.force_authenticate(user=self.admin_user)
        update_url = f'{self.url}/{self.manufacturer.id}/'
        response = self.client.put(update_url, {'phone_number': '987-654-3210'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure that the manufacturer is updated correctly
        updated_manufacturer = Manufacturer.objects.get(id=self.manufacturer.id)
        self.assertEqual(updated_manufacturer.phone_number, '987-654-3210')

    def test_manufacturer_deletion(self):
        self.client.force_authenticate(user=self.admin_user)
        # Ensure that the manufacturer deletion view returns a 204 status code
        delete_url = f'{self.url}/{self.manufacturer.id}/'
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure that the manufacturer is deleted from the database
        self.assertEqual(Manufacturer.objects.count(), 0)