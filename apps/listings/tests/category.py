from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

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

    
    def test_admin_can_create_update_delete_category(self):
        self.client.force_authenticate(user=self.admin_user)  # Authenticate as admin user

        # Create a SimpleUploadedFile for testing with a sample image
        image = SimpleUploadedFile("./images/category_hero.png", b"image", content_type="image/jpeg")

        data = {
            'name': 'Another Category',
            'image': image,
        }

        response = self.client.post('/listings/category/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        category = Category.objects.get(name='Another Category')
        self.assertIsNotNone(category.image)  # Ensure the image is saved

        # Rest of the test remains unchanged...

    def test_retrieve_category_with_image(self):
        self.client.force_authenticate(user=self.admin_user)  # Authenticate as admin user

        # Create a SimpleUploadedFile for testing with a sample image
        image = SimpleUploadedFile("./images/category_hero.png", b"image", content_type="image/jpeg")

        data = {
            'name': 'Category with Image',
            'image': image,
        }

        # Create a category with an image
        response = self.client.post('/listings/category/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        category_id = response.data['id']

        # Retrieve the category and ensure the image URL is present in the response
        response = self.client.get(f'/listings/category/{category_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image', response.data)