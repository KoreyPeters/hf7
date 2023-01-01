from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from .models import HfUser, Activity, Criterion, Category, Configuration, Survey


class ActivityAdmin(ModelAdmin):
    list_display = ["kind", "user"]
    list_filter = ["kind"]


admin.site.register(HfUser, UserAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Category)
admin.site.register(Configuration)
admin.site.register(Criterion)
admin.site.register(Survey)
