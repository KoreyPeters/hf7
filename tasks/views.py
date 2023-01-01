from rest_framework import authentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from utilities.mailer import send_simple_message
from utilities.models import Survey, HfUser


@api_view(["POST"])
@authentication_classes([authentication.TokenAuthentication])
def survey_initiated(request):
    data = request.data
    user = HfUser.objects.get(id=data["user_id"])
    survey = Survey.objects.create(
        activity_id=data["activity_id"], user_id=data["user_id"]
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
    return Response()
