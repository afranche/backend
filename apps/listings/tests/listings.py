from rest_framework import status

from apps.listings.tests.utils import BaseTestCase


class ListingViewSetTestCase(BaseTestCase):

    def test_client_can_retrieve_listings(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get('/listings/product/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_cannot_create_update_delete_listings(self):
        self.client.force_authenticate(user=self.client_user)
        data = {
            'product': {
                'name': 'New Product', 'manufacturer': 'New Manufacturer', 'price': 20.0,},
            'additional_price': 5.0,
            'characteristics': [
                {'label': 'Characteristic 1', 'type': 'input'},
                {'label': 'Pick a color', 'type': 'choices', 'choices': [
                    {'name': 'Blue', 'images': [{"image": self.get_image()}, {"image": self.get_image()}]},
                    {'name': 'Red', 'images': [{"image": self.get_image()}, {"image": self.get_image()}]},
                ]}
            ],
            'categories': [{"id": self.category1.id}],
        }

        response = self.client.post('/listings/product/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(f'/listings/product/{self.listing1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(f'/listings/product/{self.listing1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_update_delete_listings(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'product': {
                'name': 'New Product', 'manufacturer': 'New Manufacturer', 'price': 20.0,},
            'additional_price': 5.0,
            'characteristics': [
                {'label': 'Characteristic 1', 'type': 'input'},
                {'label': 'Pick a color', 'type': 'choices', 'choices': [
                    {'name': 'Blue', 'images': [{"image": self.get_image()}, {"image": self.get_image()}]},
                    {'name': 'Red', 'images': [{"image": self.get_image()}, {"image": self.get_image()}]},
                ]}
            ],
            'categories': [{"id": self.category1.id}],
        }

        response = self.client.post('/listings/product/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        listing_id = response.data['id']

        data['additional_price'] = 8.0
        data['characteristics'][0]['label'] = 'Updated characteristic'
        data['characteristics'][0]['choices'] = [{
            'name': 'Purple',
            'images': [{"image": self.get_image()}]
        }]

        data = {
            'additional_price': 8.0,
            'characteristics': [
                {'label': 'Updated characteristic', 'type': 'input'},
            ],
        }

        response = self.client.put(f'/listings/product/{listing_id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(f'/listings/product/{listing_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_listings_without_specific_characteristics(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'product': {
                'name': 'New Product', 'manufacturer': 'New Manufacturer', 'price': 20.0,},
            'additional_price': 5.0,
            'characteristics': [
                {'label': 'default', 'type': 'default', 'choices':[
                    {'name': 'default',
                     'images': [{"image": self.get_image(),}],
                     'stock': 3,
                     'is_available': False}
                ]},
            ],
            'categories': [{"id": self.category1.id}],
        }

        response = self.client.post('/listings/product/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['characteristics'][0]['label'], 'default')
        self.assertEqual(response.data['characteristics'][0]['type'], 'default')
        self.assertEqual(response.data['characteristics'][0]['choices'][0]['name'], 'default')
        self.assertEqual(response.data['characteristics'][0]['choices'][0]['stock'], 3)
        self.assertEqual(response.data['characteristics'][0]['choices'][0]['is_available'], False)