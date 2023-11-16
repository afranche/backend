from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from apps.listings.models import Coupon, Listing, Product

from apps.users.models import Address, Client

class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.user = Client.objects.create_user(
            email="email@email.com",
            password="password",
            address=Address.objects.create(
                street="street",
                city="city",
                country="usa",
                zip_code="00000",
            ),
        )
        self.client.force_authenticate(user=self.user)
        self.listings= [
            Listing.objects.create(product=Product.objects.create(
                name="Test Product",
                description="Test Description",
                price=100.0,
            ), additional_price=50.0),
            Listing.objects.create(product=Product.objects.create(
                name="Test Product 2",
                description="Test Description 2",
                price=80.0,
            ), additional_price=40.0),
        ]
        self.valid_coupon = Coupon.objects.create(code='TESTCOUPON', discount=15.0)
        self.invalid_coupon = Coupon.objects.create(code='TESTCOUPON2', discount=15.0, expiration_date='2021-01-01')
    
    def tearDown(self) -> None:
        Coupon.objects.all().delete()
        Client.objects.all().delete()
        Listing.objects.all().delete()
        Product.objects.all().delete()
        return super().tearDown()

    # test create orderwithout coupon via api
    def test_create_order_without_coupon_via_api(self):
        # Send a POST request to create an order
        data = {
            "email": "email@email.com",
            'address': {
                'street': 'street',
                'city': 'city',
                'country': 'usa',
                'zip_code': '00000',
            },
            "listings": [
                self.listings[0].id,
            ],
        }

        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_order_with_coupon_via_api(self):

        # Send a POST request to create an order with a coupon
        data = {
            "email": "test@example.com",
            'address': {
                'street': 'street',
                'city': 'city',
                'country': 'usa',
                'zip_code': '00000',
            },
            "listings": [
                self.listings[0].id,
            ],
            "coupon": self.valid_coupon.code
        }

        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Fetch the order details and check if the total price is calculated correctly
        order_id = response.data.get('id')
        order_details = self.client.get(f'/api/orders/{order_id}/').data

        # Get the total price from the API response
        total_price_from_api = order_details.get('total_price')

        # Calculate the expected total price after applying the coupon
        expected_price = 50.0 * (1 - self.coupon.discount / 100)  # Assuming the listing price minus the coupon discount

        # Compare the total price with the expected value
        self.assertEqual(total_price_from_api, expected_price)
    
    # test update order via api
    def test_update_order_via_api(self):
        # Send a POST request to create an order
        data = {
            "email": "email@email.com",
            'address': {
                'street': 'street',
                'city': 'city',
                'country': 'usa',
                'zip_code': '00000',
            },
            "listings": [
                 self.listings[0].id,
            ],
        }

        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Fetch the order details and check if the total price is calculated correctly
        order_id = response.data.get('id')
        order_details = self.client.get(f'/api/orders/{order_id}/').data

        # Get the total price from the API response
        total_price_from_api = order_details.get('total_price')

        # Calculate the expected total price after applying the coupon
        expected_price = 150.0

        # Compare the total price with the expected value
        self.assertEqual(total_price_from_api, expected_price)

        # Send a PUT request to update the order
        data = {
            "email": "changed@email.com",
            'address': {
                'street': 'changed',
                'city': 'changed',
                'country': 'FRA',
            },
            'listings': [
                self.listings[0].id,
                self.listings[1].id,
            ],
        }

        response = self.client.put(f'/api/orders/{order_id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Fetch the order details and check if the total price is calculated correctly
        order_id = response.data.get('id')
        order_details = self.client.get(f'/api/orders/{order_id}/').data

        # Get the total price from the API response
        total_price_from_api = order_details.get('total_price')

        # Calculate the expected total price after applying the coupon
        expected_price = 270.0

        # Compare the total price with the expected value
        self.assertEqual(total_price_from_api, expected_price)


# test invalid case when listings are empty via API
    def test_create_order_with_empty_listings_via_api(self):
        # Send a POST request to create an order
        data = {
            "email": "email@email.com",
            'address': {
                'street': 'street',
                'city': 'city',
                'country': 'usa',
                'zip_code': '00000',
            },
            "listings": [],
        }

        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['listings'][0], 'You should order at least one product')

# test invalid case when coupons are used more than once via API

    def test_create_order_with_coupon_used_more_than_once_via_api(self):


        # Send a POST request to create an order with a coupon
        data = {
            "email": "email@email.com",
            'address': {
                'street': 'street',
                'city': 'city',
                'country': 'usa',
                'zip_code': '00000',
            },
            "listings": [
                 self.listings[0].id,
            ],
            "coupon": [
                 self.valid_coupon.code,
                 self.valid_coupon.code
            ]
        }

        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['coupons'][0], 'You can\'t use the same coupon twice')

# test invalid case when coupons are expired via API
    
    def test_create_order_with_expired_coupon_via_api(self):
    
            # Send a POST request to create an order with a coupon
            data = {
                "email": "email@email.com",
                'address': {
                    'street': 'street',
                    'city': 'city',
                    'country': 'usa',
                    'zip_code': '00000',
                },
                "listings": [],
                "coupon": self.invalid_coupon.code
            }

            response = self.client.post('/api/orders/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
