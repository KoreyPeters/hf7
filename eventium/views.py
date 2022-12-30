import pendulum
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from eventium.forms import EventForm
from eventium.models import Event, EventCategory
from utilities.models import Category, Activity, HfUser


def home(request):
    return render(request, "eventium/home.html", locals())


def events_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    can_check_in = False
    if event.created_at > pendulum.now() - pendulum.duration(hours=2):
        can_check_in = True
    return render(request, "eventium/events_detail.html", locals())


def events_finalize(request, event_id):
    # Roll up all surveys
    # Determine final event score
    # Assign score to all participants
    # Assign score to organizer
    pass


def events_list(request):
    if request.method == "POST" and request.user.is_authenticated:
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            Activity.objects.create(
                kind=Activity.ActivityKind.EVENT_ORGANIZER,
                url=reverse("eventium-events-detail", args=[event.id]),
                user=request.user,
                entity=event.id,
            )
            try:
                category = Category.objects.get(name="Event")
                EventCategory.objects.create(event=event, category=category)
            except Category.DoesNotExist:
                pass
            return redirect("eventium-events-detail", event_id=event.id)
    else:
        if request.user.is_authenticated:
            form = EventForm()
        events = Event.objects.filter(
            created_at__gt=(pendulum.now() - pendulum.duration(days=30))
        ).order_by("-created_at")[:50]
        return render(request, "eventium/events_list.html", locals())


def events_checkin(request, event_id, attendee_id):
    event = get_object_or_404(Event, id=event_id)
    attendee = get_object_or_404(HfUser, id=attendee_id)
    if event.created_at > pendulum.now() - pendulum.duration(hours=2):
        if attendee == event.organizer:
            messages.error(
                request,
                "The event organizer is already attending by default. They do not need to be checked in.",
            )
        elif request.user == attendee and not event.allow_self_check_in:
            messages.warning(
                request,
                "You cannot check yourself into this event. Please contact the event organizer to check you in.",
            )
        else:
            try:
                Activity.objects.get(
                    user=attendee.id,
                    kind=Activity.ActivityKind.EVENT_ATTENDANCE,
                    entity=event.id,
                )
                messages.error(
                    request,
                    f"{attendee.safe_username()} is already attending this event",
                )
            except Activity.DoesNotExist:
                Activity.objects.create(
                    user=attendee,
                    kind=Activity.ActivityKind.EVENT_ATTENDANCE,
                    url=reverse("eventium-events-detail", args=[event.id]),
                    entity=event.id,
                )

                messages.success(
                    request,
                    f"{attendee.safe_username()} has been checked in to {event.name}",
                )
        return redirect(reverse("eventium-events-detail", args=[event.id]))
    else:
        messages.error(request, "Something went wrong.")
        return redirect(reverse("eventium-events-detail", args=[event.id]))
