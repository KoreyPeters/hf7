import orjson
import pendulum
import sesame
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import FormView

from eventium.models import Event
from .forms import EmailLoginForm
from .mailer import send_simple_message
from .models import Survey, Criterion


class EmailLoginView(FormView):
    template_name = "utilities/email_login.html"
    form_class = EmailLoginForm

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        User = get_user_model()
        user = User.objects.get(email=email)

        link = reverse("profile")
        link += sesame.utils.get_query_string(user)
        send_simple_message(
            user.email,
            "Magic Link for Human Flourishing (HF)",
            f"Please use the following link to log in.\nhttps://localhost:8000{link}",
        )
        print("magic link:" + link)
        return render(self.request, "utilities/email_login_success.html")


def profile(request, user_id=None):
    ask_to_check_in = False
    profile_owned_by_user = True
    if request.user.is_authenticated:
        if user_id:
            if request.user.id != user_id:
                profile_owned_by_user = False
                recent_event = (
                    Event.objects.filter(
                        organizer=request.user,
                        created_at__gt=pendulum.now() - pendulum.duration(hours=2),
                    )
                    .order_by("-created_at")
                    .first()
                )

                if recent_event:
                    ask_to_check_in = True

        user = request.user
        activities = user.activities.all()[:10]
        events = user.organized.order_by("-created_at")[:10]
        events = Event.objects.filter(organizer=user)
        return render(request, "utilities/profile.html", locals())
    else:
        return redirect("landing")


def logout_user(request):
    logout(request)
    return redirect("landing")


def landing(request):
    return render(request, "utilities/landing.html", locals())


def survey_list(request):
    surveys = request.user.surveys.order_by("-created_at")[:10]
    return render(request, "utilities/survey_list.html", locals())


def survey_detail(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    if request.method == "POST":
        data = request.POST
        survey_result = orjson.loads(data["survey-results"])
        survey.survey_results = survey_result
        survey.completed_at = pendulum.now()
        survey.save()
        messages.success(request, "Survey was saved. Thank you for making HF better!")
        return redirect("survey-list")
    else:
        criteria = []
        if "Event" in survey.activity.kind:
            criteria = Criterion.objects.filter(
                category__eventcategory__event_id=survey.activity.entity
            )
        if not survey.survey_results:
            survey.survey_results = [
                {"id": str(c.id), "question": c.question, "response": False}
                for c in criteria
            ]
        return render(request, "utilities/survey_detail.html", locals())
