from django.test import Client, TestCase
from django.urls import reverse

import pendulum
from eventium.models import Event
from utilities.models import HfUser, Activity, Survey, Category, Criterion


# Create your tests here.
class TesCheckIn(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user1 = HfUser.objects.create_user(username="user1", password="password1")
        self.user2 = HfUser.objects.create_user(username="user2", password="password2")
        self.user3 = HfUser.objects.create_user(username="user3", password="password3")

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
        self.assertContains(r, "Something went wrong", 1, 200)

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
        self.assertContains(r, event.name, 3, 200)
        self.assertContains(
            r, f"{self.user2.safe_username()} has been checked in to", 1, 200
        )

        self.assertIsNotNone(
            Activity.objects.get(
                user=self.user2, kind=Activity.ActivityKind.EVENTIUM_EVENT_ATTENDANCE
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
        self.assertContains(r, "Check in to this event", 1, 200)
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

        r = self.client.get(reverse("eventium-events-detail", args=[event.id]))
        self.assertContains(r, "Check in to this event", 0, 200)

        r = self.client.post(
            reverse("eventium-events-checkin", args=[event.id, self.user2.id]),
            follow=True,
        )
        self.assertContains(r, "Something went wrong", 1, 200)

    def test_event_finalization(self):
        category = Category.objects.create(name="DefaultEvent")
        criterion = Criterion.objects.create(
            category=category, question="Question1", value=10
        )
        event = Event.objects.create(name="TestEvent1", organizer=self.user1)

        # Organizer
        activity1 = Activity.objects.create(
            kind=Activity.ActivityKind.EVENTIUM_EVENT_ORGANIZER,
            url="/",
            user=self.user1,
            entity=event.id,
        )

        # Attendee 1
        activity2 = Activity.objects.create(
            kind=Activity.ActivityKind.EVENTIUM_EVENT_ATTENDANCE,
            url="/",
            user=self.user2,
            entity=event.id,
        )
        Survey.objects.create(
            activity_id=activity2.id,
            completed_at=pendulum.now(),
            entity=event.id,
            survey_results=[
                {
                    "id": str(criterion.id),
                    "question": criterion.question,
                    "response": True,
                }
            ],
            user_id=self.user2.id,
        )

        # Attendee 2
        activity3 = Activity.objects.create(
            kind=Activity.ActivityKind.EVENTIUM_EVENT_ATTENDANCE,
            url="/",
            user=self.user3,
            entity=event.id,
        )
        Survey.objects.create(
            activity_id=activity3.id,
            completed_at=pendulum.now(),
            entity=event.id,
            survey_results=[
                {
                    "id": str(criterion.id),
                    "question": criterion.question,
                    "response": False,
                }
            ],
            user_id=self.user2.id,
        )

        self.client.post(reverse("tasks-finalize-event"), data={"event_id": event.id})

        event.refresh_from_db()
        # confirm the event is finalized
        self.assertIsNotNone(event.finalized_at)
        # confirm event rating
        self.assertEqual(5, event.rating)
        # Reward the organizer
        activity1.refresh_from_db()
        self.assertEqual(2, activity1.points)
        # Award points to all attendees
        activity2.refresh_from_db()
        self.assertEqual(5, activity2.points)
        activity3.refresh_from_db()
        self.assertEqual(5, activity3.points)

        # Point total has rolled up
        self.user1.refresh_from_db()
        self.assertEqual(2, self.user1.points)
        self.user2.refresh_from_db()
        self.assertEqual(5, self.user2.points)
        self.user3.refresh_from_db()
        self.assertEqual(5, self.user3.points)

    def test_event_finalization_only_completed_surveys(self):
        category = Category.objects.create(name="DefaultEvent")
        criterion = Criterion.objects.create(
            category=category, question="Question1", value=10
        )
        event = Event.objects.create(name="TestEvent1", organizer=self.user1)

        # Organizer
        activity1 = Activity.objects.create(
            kind=Activity.ActivityKind.EVENTIUM_EVENT_ORGANIZER,
            url="/",
            user=self.user1,
            entity=event.id,
        )

        # Attendee 1
        activity2 = Activity.objects.create(
            kind=Activity.ActivityKind.EVENTIUM_EVENT_ATTENDANCE,
            url="/",
            user=self.user2,
            entity=event.id,
        )
        Survey.objects.create(
            activity_id=activity2.id,
            completed_at=pendulum.now(),
            entity=event.id,
            survey_results=[
                {
                    "id": str(criterion.id),
                    "question": criterion.question,
                    "response": True,
                }
            ],
            user_id=self.user2.id,
        )

        # Attendee 2
        activity3 = Activity.objects.create(
            kind=Activity.ActivityKind.EVENTIUM_EVENT_ATTENDANCE,
            url="/",
            user=self.user3,
            entity=event.id,
        )
        Survey.objects.create(
            activity_id=activity3.id,
            completed_at=None,
            entity=event.id,
            survey_results=[
                {
                    "id": str(criterion.id),
                    "question": criterion.question,
                    "response": False,
                }
            ],
            user_id=self.user2.id,
        )

        self.client.post(reverse("tasks-finalize-event"), data={"event_id": event.id})

        event.refresh_from_db()
        # confirm the event is finalized
        self.assertIsNotNone(event.finalized_at)
        # confirm event rating
        self.assertEqual(10, event.rating)
        # Reward the organizer
        activity1.refresh_from_db()
        self.assertEqual(4, activity1.points)
        # Award points to all attendees
        activity2.refresh_from_db()
        self.assertEqual(10, activity2.points)
        activity3.refresh_from_db()
        self.assertEqual(10, activity3.points)

        # Point total has rolled up
        self.user1.refresh_from_db()
        self.assertEqual(4, self.user1.points)
        self.user2.refresh_from_db()
        self.assertEqual(10, self.user2.points)
        self.user3.refresh_from_db()
        self.assertEqual(10, self.user3.points)
