from django.urls import reverse
from rest_framework import status
from apps.listings.models import Listing, Manufacturer

from apps.listings.tests.utils import BaseTestCase

class ListingDeleteTests(BaseTestCase):
    url = "/listings/product"
    def test_delete_products_in_listings(self):
        self.client.force_authenticate(self.admin_user)
        response = self.create_legit_listing()
        listing_id = response.data['id']
        response = self.client.delete(f'{self.url}/{listing_id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Listing.objects.count(), 1)
        self.assertFalse(Listing.objects.filter(id=listing_id).first().is_active)
        self.assertEqual(Listing.objects.filter(id=listing_id).first().products.count(), 0)


    def test_delete_sold_products_in_listings(self):
        self.client.force_authenticate(self.admin_user)
        response = self.create_listing_sold_products()
        listing_id = response.data['id']
        response = self.client.delete(f'{self.url}/{listing_id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Listing.objects.count(), 1)
        self.assertFalse(Listing.objects.filter(id=listing_id).first().is_active)
        # since they have been sold, they are now archived
        self.assertEqual(Listing.objects.filter(id=listing_id).first().products.count(), 5)
        self.assertFalse(any([product.is_active for product in Listing.objects.filter(id=listing_id).first().products.all()]))

