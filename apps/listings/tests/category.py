from apps.listings.tests.utils import BaseTestCase
from rest_framework import status

from apps.listings.models import Category


class CategoryViewSetTestCase(BaseTestCase):
    def test_admin_can_create_update_delete_category(self):
        self.client.force_authenticate(user=self.admin_user)
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
        self.client.force_authenticate(user=self.client_user)
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