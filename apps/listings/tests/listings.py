from rest_framework.test import APITestCase
from rest_framework import status

from apps.listings.models import Listing, Product, Characteristic, Category
from apps.users.models import Client

class ListingViewSetTestCase(APITestCase):
    def setUp(self):
        # Create a regular user
        self.client_user = Client.objects.create_user(email='client@outlook.pl', password='client_password')

        # Create an admin user
        self.admin_user = Client.objects.create_superuser(email='admin@palestinement.pl', password='admin_password')

        # Create some listings
        product1 = Product.objects.create(name='Product 1', manufacturer='Manufacturer 1', price=10.0)
        product2 = Product.objects.create(name='Product 2', manufacturer='Manufacturer 2', price=20.0)
        self.category1 = Category.objects.create(name='Category 1')
        characteristic_1 = Characteristic.objects.create(label="Characteristic 1", type="input")
        self.listing1 = Listing.objects.create(product=product1, additional_price=10.0)
        self.listing1.characteristics.add(characteristic_1)
        self.listing1.categories.add(self.category1)
        self.listing1.save()
        self.listing2 = Listing.objects.create(product=product2, additional_price=15.0)

    def tearDown(self) -> None:
        self.client_user.delete()
        self.admin_user.delete()
        Listing.objects.all().delete()
        Product.objects.all().delete()
        Characteristic.objects.all().delete()
        return super().tearDown()

    def test_client_can_retrieve_listings(self):
        # Authenticate as a regular user (client)
        self.client.force_authenticate(user=self.client_user)

        response = self.client.get('/listings/product/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_cannot_create_update_delete_listings(self):
        # Authenticate as a regular user (client)
        self.client.force_authenticate(user=self.client_user)

        data = {
            'product': {'name': 'New Product', 'manufacturer': 'New Manufacturer', 'price': 20.0},
            'additional_price': 5.0,
            'characteristics': [
                {'label': 'Characteristic 1', 'type': 'input'},
                {'label': 'Pick a color', 'type': 'choices', 'choices': ['red', 'green', 'blue']}
            ],
            'categories': [{"id": self.category1.id}]
        }

        # Try to create a new listing (POST request)
        response = self.client.post('/listings/product/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try to update an existing listing (PUT request)
        response = self.client.put(f'/listings/product/{self.listing1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try to delete a listing (DELETE request)
        response = self.client.delete(f'/listings/product/{self.listing1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_update_delete_listings(self):
        # Authenticate as an admin user
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'product': {'name': 'New Product', 'manufacturer': 'New Manufacturer', 'price': 20.0},
            'additional_price': 5.0,
            'characteristics': [
                {'label': 'Characteristic 1', 'type': 'input'},
                {'label': 'Pick a color', 'type': 'choices', 'choices': ['red', 'green', 'blue']}
            ],
            'categories': [{"id": self.category1.id}]
        }

        # Admin can create a new listing (POST request)
        response = self.client.post('/listings/product/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        listing_id = response.data['id']

        # Admin can update an existing listing (PUT request)
        data['additional_price'] = 8.0
        data['characteristics'][0]['label'] = 'Updated characteristic'
        response = self.client.put(f'/listings/product/{listing_id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Admin can delete a listing (DELETE request)
        response = self.client.delete(f'/listings/product/{listing_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)