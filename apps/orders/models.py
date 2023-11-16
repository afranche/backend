from django.db import models
from django.utils.translation import gettext as _

from apps.listings.models import Coupon


class Order(models.Model):
    email = models.EmailField(
        _("email address"),
    )
    address = models.ForeignKey(
        "users.Address", blank=True, null=True, on_delete=models.PROTECT
    )
    class OrderStatus(models.TextChoices):
        PAID = "paid", "Paid"
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        RECEIVED = "received", "Received"
        CANCELED = "canceled", "Canceled"

    listings = models.ManyToManyField('Listing', through='OrderListing')
    status = models.CharField(
        _("Order Status"),
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.DRAFT
    )
    comment = models.TextField(_("Client Comment"), blank=True, null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Field for storing total price

    def save(self, *args, **kwargs):
        # Calculate the total price here before saving
        self.shipping_fee = self.compute_shipping_fee()  # Call your compute_shipping_fee method
        self.total_price = self.get_total_price()  # Call your get_total_price method
        super().save(*args, **kwargs)

    def compute_shipping_fee(self):
        pass

    def get_total_price(self):
        # Calculate the total price based on items, shipping fees, and coupon discounts
        total_price = sum([listing.additional_price for listing in self.listings.all()])
        total_price += self.shipping_fee
        
        if self.coupon:
            total_price -= self.coupon.discount_amount  # Assuming a discount_amount attribute in the Coupon model

        return total_price

class OrderListing(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    characteristics = models.ManyToManyField('Characteristic', through='OrderCharacteristic')

class OrderCharacteristic(models.Model):
    order_listing = models.ForeignKey(OrderListing, on_delete=models.CASCADE)
    characteristic = models.ForeignKey('Characteristic', on_delete=models.CASCADE)
    choice = models.CharField(_("Chosen Answer"), max_length=112, blank=True)
    input = models.CharField(_("Custom Input"), max_length=64, blank=True)

    def save(self, *args, **kwargs):
        if self.choice:
            self.input = ""  # Clear the input if a choice is provided
        return super().save(*args, **kwargs)
