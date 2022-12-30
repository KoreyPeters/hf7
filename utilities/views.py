from datetime import timedelta

import pendulum
import sesame
from django.contrib.auth import get_user_model, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView

from eventium.models import Event
from .forms import EmailLoginForm


class EmailLoginView(FormView):
    template_name = "utilities/email_login.html"
    form_class = EmailLoginForm

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        User = get_user_model()
        user = User.objects.get(email=email)

        link = reverse("profile")
        link += sesame.utils.get_query_string(user)
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
        return render(request, "utilities/profile.html", locals())
    else:
        return redirect("landing")


def logout_user(request):
    logout(request)
    return redirect("landing")


def landing(request):
    return render(request, "utilities/landing.html", locals())
