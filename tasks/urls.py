from django.urls import path

from . import views

urlpatterns = [
    path("survey-initiated/", views.survey_initiated, name="tasks-survey-response"),
    path("finalize-event/", views.finalize_event, name="tasks-finalize-event"),
]
