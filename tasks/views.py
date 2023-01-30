import pendulum
from rest_framework import authentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from eventium.models import Event
from utilities.mailer import send_simple_message
from utilities.models import Survey, HfUser, Criterion, Activity


@api_view(["POST"])
@authentication_classes([authentication.TokenAuthentication])
def survey_initiated(request):
    data = request.data
    user = HfUser.objects.get(id=data["user_id"])
    survey = Survey.objects.create(
        activity_id=data["activity_id"],
        entity=data["entity_id"],
        user_id=data["user_id"],
    )
    send_simple_message(
        user.email,
        "You have been offered an HF survey.",
        "Surveys help us to know what people and organizations are doing their best to advance human flourishing. "
        "You have been issued a survey for a recent activity. Click the following link to go to the survey directly, or "
        f"log in to https://www.humanflourishing.online and click 'Surveys' from the navigation bar at the top of the "
        f"page.\nhttps://www.humanflourishing.online/profile/surveys/{survey.id}/",
    )
    return Response()


@api_view(["POST"])
@authentication_classes([authentication.TokenAuthentication])
def finalize_event(request):
    data = request.data
    event = Event.objects.get(id=data["event_id"])

    # Roll up all surveys
    surveys = Survey.objects.filter(entity=event.id, completed_at__isnull=False)
    survey_results = {}
    for survey in surveys:
        for result in survey.survey_results:
            if result["id"] in survey_results:
                survey_results[result["id"]]["count"] = (
                    survey_results[result["id"]]["count"] + 1
                )
                if result["response"] is True:
                    survey_results[result["id"]]["success"] = (
                        survey_results[result["id"]]["success"] + 1
                    )
            else:
                survey_results[result["id"]] = {
                    "count": 1,
                    "success": 1 if result["response"] is True else 0,
                }
    event.survey_results = survey_results

    # Determine the event's final rating
    final_rating = 0
    for criterion, result in survey_results.items():
        criterion_value = Criterion.objects.get(id=criterion).value
        success_percentage = (
            result["success"] / result["count"] if result["count"] > 0 else 0
        )
        final_rating += criterion_value * success_percentage
    event.rating = final_rating

    # Award points to all attendees
    attendee_count = 0
    attendees = Activity.objects.filter(
        entity=event.id, kind=Activity.ActivityKind.EVENTIUM_EVENT_ATTENDANCE
    )
    for activity in attendees:
        activity.points = event.rating
        activity.save()
        attendee_count += 1

    # Reward the organizer
    organizer = Activity.objects.get(user=event.organizer, entity=event.id)
    organizer.points = (event.rating * attendee_count) * 0.2
    organizer.save()

    # Mark the event finalized
    event.finalized_at = pendulum.now()
    event.save()

    return Response()
