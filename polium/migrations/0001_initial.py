# Generated by Django 4.1.4 on 2023-01-21 18:24

from django.db import migrations, models
import django.db.models.deletion
import django_ulid.models
import pendulum
import utilities.modelfields
import utilities.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Politician",
            fields=[
                (
                    "id",
                    django_ulid.models.ULIDField(
                        default=utilities.models.new_ulid,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    utilities.modelfields.PendulumDateTimeField(default=pendulum.now),
                ),
                ("first_name", models.CharField(max_length=250)),
                ("last_name", models.CharField(max_length=250)),
                ("rating", models.IntegerField(default=0)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Race",
            fields=[
                (
                    "id",
                    django_ulid.models.ULIDField(
                        default=utilities.models.new_ulid,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    utilities.modelfields.PendulumDateTimeField(default=pendulum.now),
                ),
                ("name", models.CharField(max_length=250)),
                ("date", utilities.modelfields.PendulumDateField(default=pendulum.now)),
                (
                    "location",
                    models.CharField(
                        help_text="Please provide a common/helpful location for this race.",
                        max_length=250,
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("Federal", "Federal"),
                            ("Regional (State/Province)", "Regional"),
                            ("Municipal", "Municipal"),
                        ],
                        max_length=50,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Candidate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    utilities.modelfields.PendulumDateTimeField(default=pendulum.now),
                ),
                (
                    "politician",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="polium.politician",
                    ),
                ),
                (
                    "race",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="polium.race"
                    ),
                ),
            ],
        ),
    ]
