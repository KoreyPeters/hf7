from django.urls import path
from . import views

urlpatterns = [
    path("management", views.cr_management, name="cr_management"),
    path("surveys", views.survey_list, name="survey-list"),
    path("surveys/<survey_id>", views.survey_detail, name="survey-detail"),
    path("<user_id>", views.profile, name="profile-detail"),
    path("", views.profile, name="profile"),
]
