from django.urls import path

from . import views

urlpatterns = [
    path("", views.home),
    path("events/", views.events_list, name="eventium-events-list"),
    path("events/<event_id>", views.events_detail, name="eventium-events-detail"),
    path(
        "events/<event_id>/checkin/<attendee_id>",
        views.events_checkin,
        name="eventium-events-checkin",
    ),
    path(
        "events/<event_id>/finalize",
        views.events_finalize,
        name="eventium-events-finalize",
    ),
]
