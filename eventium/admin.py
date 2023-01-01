from django.contrib import admin

from eventium.models import Event, EventCategory

admin.site.register(Event)
admin.site.register(EventCategory)
