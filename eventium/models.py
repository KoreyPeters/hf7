import pendulum as pendulum
from django.conf import settings
from django.db import models
from django_ulid.models import default, ULIDField

from utilities.models import Category


def new_ulid():
    return str(default())


# Create your models here.
class Event(models.Model):
    id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    created_at = models.DateTimeField(default=pendulum.now)
    name = models.CharField(max_length=250)
    values = models.IntegerField(default=0)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    allow_self_check_in = models.BooleanField(default=True)


class EventCategory(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=pendulum.now)
