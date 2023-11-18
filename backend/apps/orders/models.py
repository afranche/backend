from django.db import models
from django.utils.translation import gettext as _

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

    # fetch the products like so: self.items (fk in Product model)

    email = models.EmailField(
        _("email address"),
    )
    address = models.ForeignKey(
        "users.Address", blank=True, null=True, on_delete=models.PROTECT
    )

    status = models.SmallIntegerField(_('status'), choices=STATUS_CHOICES, default=1)  # type: ignore
    client = models.ForeignKey('users.Client', blank=True, null=True, on_delete=models.PROTECT)
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)

    created_at = models.DateTimeField(_('created at'), auto_now=True)
    last_update = models.DateTimeField(_('last update'), auto_now_add=True)


    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        # if client exists in order, set email to theirs. otherwise, expect email from front-end
        if self.client is not None:
            self.email = self.client.email  # type: ignore
        return super().save(force_insert, force_update, using, update_fields)