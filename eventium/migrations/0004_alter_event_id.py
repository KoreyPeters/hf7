# Generated by Django 4.1.4 on 2022-12-28 17:20

from django.db import migrations
import django_ulid.models
import eventium.models


class Migration(migrations.Migration):

    dependencies = [
        ("eventium", "0003_alter_event_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="id",
            field=django_ulid.models.ULIDField(
                default=eventium.models.new_ulid,
                editable=False,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
