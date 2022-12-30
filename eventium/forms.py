from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from eventium.models import Event


class EventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-event-create"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "/eventium/events/"

        self.helper.add_input(Submit("submit", "Create Event"))

    class Meta:
        model = Event
        fields = ["name", "allow_self_check_in"]
