from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import Client, Address

class ManageOnlyYourOwnTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_user = Client.objects.create_superuser(email='admin@palestinement.pl', password='admin_password')
        self.normal_user = Client.objects.create_user(email='client@outlook.pl', password='client_password')

    def tearDown(self) -> None:
        self.admin_user.delete()
        self.normal_user.delete()
        Client.objects.all().delete()
        Address.objects.all().delete()  # type: ignore
        return super().tearDown()

    def test_admin_can_create(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            '/auth/client/',
            {'email': 'blurp@blurp.blurp', 'password1': 'blurp_password', 'password2': 'blurp_password',
             'address': {
                'name': 'home',
                'address1': '2 street',
                'address2': 'building 2',
                'zip_code': '00000',
                'region': 'mazowieckie',
                'city': 'Warszawa',
                'country': 'FRA'
             }}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # type: ignore

    def test_normal_user_can_create(self):
        self.client.force_authenticate(user=self.normal_user)

        response = self.client.post(
            '/auth/client/',
            {'email': 'blurp@blurp.blurp', 'password1': 'blurp_password', 'password2': 'blurp_password',
             'address': {
                'name': 'home',
                'address1': '2 street',
                'address2': 'building 2',
                'zip_code': '00-000',
                'region': 'mazowieckie',
                'city': 'Warszawa',
                'country': 'PL'
             }}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # type: ignore

    def test_normal_user_cannot_get(self):
        # normal user should not be able to see other customer's data
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get('/auth/client/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # type: ignore

    def test_admin_can_get(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/auth/client/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # type: ignore

    def test_normal_user_can_update_own_object(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.put(f'/auth/client/{self.normal_user.pk}/', {'email': 'varsovie@mdr.pl'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # type: ignore

    def test_normal_user_cannot_update_other_objects(self):
        other_user = Client.objects.create_user(email="other_user@other-dontcheat.pl", password="otherpassword")
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.put(f'/auth/client/{other_user.pk}/', {'first_name': 'you stinks'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # type: ignore

    def test_normal_user_can_delete_own_object(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.delete(f'/auth/client/{self.normal_user.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)  # type: ignore

    def test_normal_user_cannot_delete_other_objects(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.delete(f'/auth/client/{self.admin_user.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # type: ignore