import pendulum
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django_ulid.models import default, ULIDField

from utilities.modelfields import PendulumDateTimeField


def new_ulid():
    return default()


class HfUser(AbstractUser):
    id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    points = models.IntegerField(default=0)

    def safe_username(self):
        if self.username:
            return self.username
        else:
            return f"{self.email[:1]}****@{self.email.split('@')[-1]}"


class Configuration(models.Model):
    event_organizer_point_share = models.IntegerField(
        help_text="The percentage of all points the organizer earns", default=20
    )
    survey_percentage = models.IntegerField(
        help_text="A value between 0 and 100", default=10
    )
    event_check_in_cutoff_hours = models.IntegerField(
        help_text="How old in hours an event can still be checked in to", default=2
    )


class Activity(models.Model):
    class ActivityKind(models.TextChoices):
        EVENT_ATTENDANCE = "Event attendance"
        EVENT_ORGANIZER = "Event organizer"

    id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    created_at = PendulumDateTimeField(default=pendulum.now)
    kind = models.CharField(choices=ActivityKind.choices, max_length=20)
    points = models.IntegerField(default=0)
    url = models.CharField(max_length=250)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activities"
    )
    entity = ULIDField()


class Category(models.Model):
    id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    created_at = PendulumDateTimeField(default=pendulum.now)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class Criterion(models.Model):
    id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    created_at = PendulumDateTimeField(default=pendulum.now)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question = models.TextField()
    value = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.question[:30]}..." if len(self.question) > 40 else self.question
