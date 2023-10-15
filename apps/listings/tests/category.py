from rest_framework.test import APITestCase
from rest_framework import status

from apps.listings.models import Category
from apps.users.models import Client

class CategoryViewSetTestCase(APITestCase):
    def setUp(self):
        # Create an admin user
        self.admin_user = Client.objects.create_superuser(email='admin@palestinement.pl', password='admin_password')

        # Create a regular user (Client)
        self.client_user = Client.objects.create_user(email='client@outlook.pl', password='client_password')

        # Create some categorues
        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')

    def tearDown(self) -> None:
        self.admin_user.delete()
        self.client_user.delete()
        Category.objects.all().delete()
        return super().tearDown()

    def test_admin_can_create_update_delete_category(self):
        self.client.force_authenticate(user=self.admin_user)  # Authenticate as admin user
        data = {
            'name': 'Another Category',

        }
        response = self.client.post('/listings/category/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        category = Category.objects.get(name='Another Category')
        data = {
            'name': 'Updated Category',
        }
        response = self.client.put(f'/listings/category/{category.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(f'/listings/category/{category.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_client_or_anonymous_user_can_get_category(self):
        self.client.force_authenticate(user=self.client_user)  # Authenticate as client user
        response = self.client.get('/listings/category/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_or_anonymous_user_cannot_create_update_delete_category(self):
        data = {
            'name': 'Another Category'
        }
        response = self.client.post('/listings/category/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        category = Category.objects.get(name='Category 1')
        data = {
            'name': 'Updated Category',
        }
        response = self.client.put(f'/listings/category/{category.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(f'/listings/category/{category.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)