from django.db import models
from django.utils.translation import gettext as _


class Order(models.Model):
    email = models.EmailField(
        _("email address"),
    )
    address = models.ForeignKey(
        "users.Address", blank=True, null=True, on_delete=models.PROTECT
    )
