import uuid
from datetime import datetime
from math import fsum

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext as _

STATUS_CHOICES = (
    (1, _("draft")),
    (2, _("paid")),
    (3, _("sent")),
    (4, _("cancelled")),
    (5, _("received")),
)


STATUS_CHOICES = (
    (1, _("in selection")),
    (2, _("awaiting payment")),
    (3, _("payed")),
    (4, _("confirmed")),
    (5, _("sent")),
    (6, _("completed")),
)


class Order(models.Model):
    REQUIRED_FIELDS = ["email"]

    # NOTE(djnn) fetch the products like so: self.products_set (fk in Product model)

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)

    email = models.EmailField(_("email address"))
    address = models.ForeignKey(
        "users.Address", blank=True, null=True, on_delete=models.PROTECT
    )

    status = models.SmallIntegerField(_("status"), choices=STATUS_CHOICES, default=1)  # type: ignore
    client = models.ForeignKey(
        "users.Client", blank=True, null=True, on_delete=models.PROTECT
    )
    tracking_numbers = ArrayField(
        models.CharField(max_length=128), blank=True, null=True
    )
    shipping_fee = models.FloatField(_("shipping fee"), auto_created=True, default=0.0)  # type: ignore

    created_at = models.DateTimeField(_("created at"), auto_now=True)
    last_update = models.DateTimeField(_("last update"), auto_now=True)

    selected_coupon = models.ForeignKey(
        "listings.Coupon",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="applied_to",
    )

    @property
    def total_price(self) -> float:
        full_sum = self.shipping_fee + fsum(
            [
                product.additional_price + product.listing.price
                for product in self.products_set
            ]
        )
        if not self.selected_coupon or self.selected_coupon.is_expired:
            return full_sum

        return full_sum - self.selected_coupon.discount

    def save(self, *args, **kwargs):  # type: ignore
        # if client exists in order, set email to theirs. otherwise, expect email from front-end
        # TODO: Check if the e-mail is provided and validated in ☝️ case
        if self.client is not None:
            self.email = self.client.email  # type: ignore

        """
        TODO: To write and to move elsewhere for reusability

        if self.address.country in "EU":
            match self.weight:
                case w if 1100.0 >= w:
                    self.shipping_fee = 15.0
                case w if 1900.0 >= w:
                    self.shipping_fee = 24.0
                case w if 2900.0 >= w:
                    self.shipping_fee = 30.0
                case w if 3900.0 >= w:
                    self.shipping_fee = 45.0
                case w if 4900.0 >= w:
                    self.shipping_fee = 60.0
        else:
            match self.weight:
                case w if 1100.0 >= w:
                    self.shipping_fee = 25.0
                case w if 1900.0 >= w:
                    self.shipping_fee = 35.0
                case w if 2900.0 >= w:
                    self.shipping_fee = 50.0
                case w if 3900.0 >= w:
                    self.shipping_fee = 75.0
                case w if 4900.0 >= w:
                    self.shipping_fee = 100.0
        """

        return super().save(*args, **kwargs)
