import pendulum
from django.db import models

from utilities.modelfields import PendulumDateTimeField, PendulumDateField
from utilities.models import HfModel


class Politician(HfModel):
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class Race(HfModel):
    class RaceKind(models.TextChoices):
        FEDERAL = "Federal"
        REGIONAL = "Regional (State/Province)"
        MUNICIPAL = "Municipal"

    name = models.CharField(max_length=250)
    date = PendulumDateField(default=pendulum.now)
    location = models.CharField(
        max_length=250,
        help_text="Please provide a common/helpful location for this race.",
    )
    kind = models.CharField(choices=RaceKind.choices, max_length=50)


class Candidate(models.Model):
    created_at = PendulumDateTimeField(default=pendulum.now)
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
