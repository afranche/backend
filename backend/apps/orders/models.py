from math import fsum
from django.db import models
from django.utils.translation import gettext as _
from django.contrib.postgres.fields import ArrayField

from datetime import datetime

import uuid


STATUS_CHOICES = (
        (1, _('draft')),
        (2, _('paid')),
        (3, _('sent')),
        (4, _('cancelled')),
        (5, _('received')),
    )

import uuid


STATUS_CHOICES = (
        (1, _('in selection')),
        (2, _('awaiting payment')),
        (3, _('payed')),
        (4, _('confirmed')),
        (5, _('sent')),
        (6, _('completed')),
    )


class Order(models.Model):
    REQUIRED_FIELDS = ['email']

    #NOTE(djnn) fetch the products like so: self.products_set (fk in Product model)

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)

    email = models.EmailField(_("email address"))
    address = models.ForeignKey("users.Address", blank=True, null=True, on_delete=models.PROTECT)

    status = models.SmallIntegerField(_('status'), choices=STATUS_CHOICES, default=1)  # type: ignore
    client = models.ForeignKey('users.Client', blank=True, null=True, on_delete=models.PROTECT)
    tracking_numbers = ArrayField(models.CharField(max_length=128), blank=True, null=True)
    shipping_fee = models.FloatField(_('shipping fee'), default=0.0)  # type: ignore

    created_at = models.DateTimeField(_('created at'), auto_now=True)
    last_update = models.DateTimeField(_('last update'), auto_now=True)

    selected_coupon = models.ForeignKey('listings.Coupon', on_delete=models.PROTECT, blank=True, null=True, related_name='applied_to')


    @property
    def total_price(self) -> float:
        full_sum = self.shipping_fee + fsum([product.additional_price + product.listing.price for product in self.products_set])
        if not self.selected_coupon or self.selected_coupon.is_expired:
            return full_sum

        return full_sum - self.selected_coupon.discount



    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        # if client exists in order, set email to theirs. otherwise, expect email from front-end
        if self.client is not None:
            self.email = self.client.email  # type: ignore

        # django is autistic
        self.last_update = datetime.now()
        return super().save(force_insert, force_update, using, update_fields)