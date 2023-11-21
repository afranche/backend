from django.db import models

from typing import Any


class Invoice(models.Model):
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT)
    file = models.FileField(upload_to="/invoices")
    date = models.DateField(auto_now_add=True)

    def save(self, *args: Any, **kwargs: Any):
        if self.id:  # type: ignore
            raise Exception("Invoice cannot be updated")

        return super().save(*args, **kwargs)
