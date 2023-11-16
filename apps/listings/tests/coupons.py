from datetime import timedelta, datetime
from rest_framework.test import APITestCase
from rest_framework import status

from apps.listings.models import Coupon, Listing
from apps.users.models import Client


class CouponAPITestCase(APITestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(code="TEST", discount=10.0)
        self.user = Client.objects.create_superuser(email="blurp@clurp.lol", password="mdrmdrmdrmdr")  # Creating an admin user
        self.client.force_authenticate(user=self.user)  # Simulate authentication

    def test_create_coupon_as_admin(self):
        applied_to = Listing.objects.first()
        if not applied_to:
            applied_to = Listing.objects.create(product__name="Test Product", additional_price=10.0)
        applied_to = [applied_to.id]
        data = {'code': 'NEWCOUPON',
                'discount': 15.0,
                'applied_to': applied_to,
                'expiration_date': (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")}
        response = self.client.post('/listings/gertrude', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Additional assertions based on the expected response data or Coupon creation

    def test_get_coupons_as_admin(self):
        response = self.client.get('/listings/gertrude')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Additional assertions based on the expected response data for listing coupons

    def tearDown(self) -> None:
        Coupon.objects.all().delete()
        Client.objects.all().delete()
        Listing.objects.all().delete()
        return super().tearDown()