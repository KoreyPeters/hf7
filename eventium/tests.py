from datetime import timedelta

import pendulum
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from eventium.models import Event
from utilities.models import HfUser, Activity


# Create your tests here.
class TesCheckIn(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user1 = HfUser.objects.create_user(username="user1", password="password1")
        self.user2 = HfUser.objects.create_user(username="user2", password="password2")

    def test_root_profile_url_logged_in(self):
        self.assertTrue(self.client.login(username="user1", password="password1"))
        r = self.client.get(reverse("profile"), follow=True)
        self.assertContains(r, "Recent Activities", 1, 200)

    def test_root_profile_url_logged_out(self):
        r = self.client.get(reverse("profile"), follow=True)
        self.assertContains(r, "Welcome to HF", 1, 200)

    def test_profile_activities_visible_to_user(self):
        self.assertTrue(self.client.login(username="user1", password="password1"))
        r = self.client.get(
            reverse("profile-detail", args=[self.user1.id]), follow=True
        )
        self.assertContains(r, "Recent Activities", 1, 200)

    def test_profile_activities_hidden_to_different_user(self):
        self.assertTrue(self.client.login(username="user1", password="password1"))
        r = self.client.get(
            reverse("profile-detail", args=[self.user2.id]), follow=True
        )
        self.assertContains(r, "Recent Activities", 0, 200)

    def test_profile_hidden_unless_logged_in(self):
        r = self.client.get(
            reverse("profile-detail", args=[self.user1.id]), follow=True
        )
        self.assertContains(r, "Welcome to HF", 1, 200)

    def test_check_in_hidden_if_no_recent_event(self):
        event = Event.objects.create(
            name="TestEvent1",
            organizer=self.user1,
            created_at=pendulum.now() - pendulum.duration(hours=3),
        )
        self.assertTrue(self.client.login(username="user1", password="password1"))
        r = self.client.get(
            reverse("profile-detail", args=[self.user2.id]), follow=True
        )
        self.assertContains(r, "Would you like to check this user in", 0, 200)

        # Checking in doesn't do anything
        r = self.client.post(
            reverse("eventium-events-checkin", args=[event.id, self.user2.id]),
            follow=True,
        )
        self.assertEqual(r.status_code, 400)

    def test_check_in(self):
        event = Event.objects.create(name="TestEvent1", organizer=self.user1)
        self.assertTrue(self.client.login(username="user1", password="password1"))
        r = self.client.get(
            reverse("profile-detail", args=[self.user2.id]), follow=True
        )
        self.assertContains(r, "Would you like to check this user in", 1, 200)

        # Can check in.
        r = self.client.post(
            reverse("eventium-events-checkin", args=[event.id, self.user2.id]),
            follow=True,
        )
        self.assertContains(r, event.name, 2, 200)
        self.assertContains(
            r, f"{self.user2.safe_username()} has been checked in to", 1, 200
        )

        self.assertIsNotNone(
            Activity.objects.get(
                user=self.user2, kind=Activity.ActivityKind.EVENT_ATTENDANCE
            )
        )

    def test_organizer_cant_attend(self):
        event = Event.objects.create(name="TestEvent1", organizer=self.user1)
        self.assertTrue(self.client.login(username="user1", password="password1"))
        r = self.client.post(
            reverse("eventium-events-checkin", args=[event.id, self.user1.id]),
            follow=True,
        )
        self.assertContains(
            r, "The event organizer is already attending by default.", 1, 200
        )

    def test_self_check_in_not_allowed(self):
        event = Event.objects.create(
            name="TestEvent1", organizer=self.user1, allow_self_check_in=False
        )
        self.assertTrue(self.client.login(username="user2", password="password2"))
        r = self.client.get(reverse("eventium-events-detail", args=[event.id]))
        self.assertContains(r, "Check in to this event", 0, 200)
        r = self.client.post(
            reverse("eventium-events-checkin", args=[event.id, self.user2.id]),
            follow=True,
        )
        self.assertContains(r, "You cannot check yourself into this event.", 1, 200)

    def test_self_check_in_allowed(self):
        event = Event.objects.create(name="TestEvent1", organizer=self.user1)
        self.assertTrue(self.client.login(username="user2", password="password2"))
        r = self.client.get(reverse("eventium-events-detail", args=[event.id]))
        self.assertContains(r, "Check in to this event", 0, 200)
        r = self.client.post(
            reverse("eventium-events-checkin", args=[event.id, self.user2.id]),
            follow=True,
        )
        self.assertContains(
            r, f"{self.user2.safe_username()} has been checked in to", 1, 200
        )

    def test_self_check_in_allowed_but_expired(self):
        self.assertTrue(self.client.login(username="user1", password="password1"))
        event = Event.objects.create(
            name="TestEvent1",
            organizer=self.user1,
            created_at=pendulum.now() - pendulum.duration(hours=3),
        )
        r = self.client.post(
            reverse("eventium-events-checkin", args=[event.id, self.user2.id]),
            follow=True,
        )
        self.assertEqual(r.status_code, 400)
