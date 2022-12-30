from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import HfUser, Activity, Criterion, Category, Configuration

admin.site.register(HfUser, UserAdmin)
admin.site.register(Activity)
admin.site.register(Category)
admin.site.register(Configuration)
admin.site.register(Criterion)
