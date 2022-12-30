from django.urls import path
from . import views

urlpatterns = [
    path("", views.profile, name="profile"),
    path("<user_id>", views.profile, name="profile-detail"),
]
