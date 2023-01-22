from django.contrib import admin

from polium.models import Politician, Race, Candidate

admin.site.register(Candidate)
admin.site.register(Politician)
admin.site.register(Race)
