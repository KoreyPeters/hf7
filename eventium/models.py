import pendulum
from django.conf import settings
from django.db import models

from utilities.modelfields import PendulumDateTimeField
from utilities.models import Category, HfModel


class Event(HfModel):
    name = models.CharField(max_length=250)
    rating = models.IntegerField(default=0)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="organized",
    )
    allow_self_check_in = models.BooleanField(default=True)
    finalized_at = PendulumDateTimeField(blank=True, null=True)
    survey_results = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.created_at}"


class EventCategory(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = PendulumDateTimeField(default=pendulum.now)
