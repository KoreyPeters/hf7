from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.admin import TokenAdmin

from .models import HfUser, Activity, Criterion, Category, Configuration, Survey

TokenAdmin.raw_id_fields = ["user"]


class ActivityAdmin(ModelAdmin):
    list_display = ["kind", "user"]
    list_filter = ["kind"]


class HfUserAdmin(UserAdmin):
    list_display_links = ["email"]


class CriterionAdmin(ModelAdmin):
    list_display = ["question", "category", "value"]
    list_filter = ["category"]


admin.site.register(HfUser, UserAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Category)
admin.site.register(Configuration)
admin.site.register(Criterion, CriterionAdmin)
admin.site.register(Survey)
