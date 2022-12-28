import pendulum
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django_ulid.models import default, ULIDField


def new_ulid():
    return default()


class HfUser(AbstractUser):
    id = ULIDField(default=new_ulid, primary_key=True, editable=False)


class Activity(models.Model):
    class ActivityKind(models.TextChoices):
        EVENT_ATTENDANCE = "Event attendance"
        EVENT_ORGANIZER = "Event organizer"

    id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    created_at = models.DateTimeField(default=pendulum.now)
    kind = models.CharField(choices=ActivityKind.choices, max_length=20)
    points = models.IntegerField(default=0)
    url = models.CharField(max_length=250)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entity = ULIDField()


class Category(models.Model):
    id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    created_at = models.DateTimeField(default=pendulum.now)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)


class Criterion(models.Model):
    id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    created_at = models.DateTimeField(default=pendulum.now)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question = models.TextField()
    value = models.IntegerField(default=0)
