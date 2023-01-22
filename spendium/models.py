import pendulum
from django.db import models
from django_ulid.models import ULIDField, default
from location_field.models.plain import PlainLocationField

from utilities.modelfields import PendulumDateTimeField
from utilities.models import HfModel


def new_ulid():
    return default()


class Store(models.Model):
    id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    created_at = PendulumDateTimeField(default=pendulum.now)
    name = models.CharField(max_length=250)
    location = PlainLocationField(
        based_fields=["city"], zoom=5, default="40.17887331434696,-95.625"
    )
    place_id = models.CharField(max_length=100, blank=True, null=True)
    store_number = models.CharField(max_length=20, blank=True, null=True)

    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Purchase(HfModel):
    currency = models.CharField(max_length=3)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    payment_channel = models.CharField(max_length=10)
