from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from datetime import timedelta
from django.utils import timezone
from notes.models import Note
from tasks.models import Task


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dashboard_user', password='testpass123',)

    def test_anonymous_user_is_redirected_to_login(self):
        dashboard_url = reverse('dashboard:dashboard')
        login_url = reverse('login')

        response = self.client.get(dashboard_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{login_url}?next={dashboard_url}')

    def test_authenticated_user_can_open_dashboard(self):
        self.client.login(username='dashboard_user', password='testpass123')

        response = self.client.get(reverse('dashboard:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')


class DashboardNotesContextTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dashboard_notes_user', password='testpass123',)
        self.other_user = get_user_model().objects.create_user(username='dashboard_notes_other', password='testpass123',)

    def _create_note(self, user, label, minutes_ago):
        note = Note.objects.create(label=label, text=f'{label} text', user=user,)
        Note.objects.filter(id=note.id).update(created_at=timezone.now() - timedelta(minutes=minutes_ago))
        note.refresh_from_db()
        return note

    def test_dashboard_context_contains_recent_notes_for_current_user_only(self):
        own_oldest = self._create_note(self.user, 'Own oldest', 30)
        own_older = self._create_note(self.user, 'Own older', 20)
        own_middle = self._create_note(self.user, 'Own middle', 10)
        own_newest = self._create_note(self.user, 'Own newest', 1)
        other_newest = self._create_note(self.other_user, 'Other newest', 0)

        self.client.login(username='dashboard_notes_user', password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))

        self.assertEqual(response.status_code, 200)
        recent_notes = list(response.context['recent_notes'])

        self.assertEqual(len(recent_notes), 3)
        self.assertEqual([n.label for n in recent_notes], [own_newest.label, own_middle.label, own_older.label])
        self.assertNotIn(own_oldest, recent_notes)
        self.assertNotIn(other_newest, recent_notes)
        self.assertTrue(all(n.user_id == self.user.id for n in recent_notes))


class DashboardTasksContextTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dashboard_tasks_user', password='testpass123',)
        self.other_user = get_user_model().objects.create_user(username='dashboard_tasks_other', password='testpass123',)

    def _create_task(self, user, label, hours_delta, status=False):
        return Task.objects.create(label=label, description=f'{label} description', priority=2,
            deadline=timezone.now() + timedelta(hours=hours_delta), status=status, user=user,)

    def test_dashboard_context_contains_upcoming_tasks_for_current_user_only(self):
        own_near = self._create_task(self.user, 'Own near', 1)
        own_middle = self._create_task(self.user, 'Own middle', 3)
        own_far = self._create_task(self.user, 'Own far', 5)
        own_extra = self._create_task(self.user, 'Own extra', 7)

        self._create_task(self.user, 'Own completed', 2, status=True)
        self._create_task(self.user, 'Own past', -1)
        self._create_task(self.other_user, 'Other near', 0.5)

        self.client.login(username='dashboard_tasks_user', password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))

        self.assertEqual(response.status_code, 200)
        upcoming_tasks = list(response.context['upcoming_tasks'])

        self.assertEqual(len(upcoming_tasks), 3)
        self.assertEqual([t.label for t in upcoming_tasks], [own_near.label, own_middle.label, own_far.label])
        self.assertNotIn(own_extra, upcoming_tasks)
        self.assertTrue(all(t.user_id == self.user.id for t in upcoming_tasks))
        self.assertTrue(all(t.status is False for t in upcoming_tasks))
        self.assertTrue(all(t.deadline >= timezone.now() for t in upcoming_tasks))


class DashboardStatisticsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dashboard_stats_user', password='testpass123',)
        self.other_user = get_user_model().objects.create_user(username='dashboard_stats_other', password='testpass123',)

    def _local_noon(self, days_ago):
        from datetime import datetime, time

        day = timezone.localdate() - timedelta(days=days_ago)
        naive = datetime.combine(day, time(hour=12, minute=0))
        return timezone.make_aware(naive, timezone.get_current_timezone())

    def _create_completed_task(self, user, label, days_ago):
        return Task.objects.create(label=label, description=f'{label} description', priority=2,
            deadline=timezone.now() + timedelta(days=1), status=True, completed_at=self._local_noon(days_ago), user=user,)

    def test_dashboard_context_contains_correct_productivity_stats(self):
        self._create_completed_task(self.user, 'Today one', 0)
        self._create_completed_task(self.user, 'Today two', 0)
        self._create_completed_task(self.user, 'Yesterday one', 1)
        self._create_completed_task(self.user, 'Six days ago one', 6)

        self._create_completed_task(self.user, 'Too old', 8)
        self._create_completed_task(self.other_user, 'Other user today', 0)
        Task.objects.create(label='Not completed', description='Not completed description', priority=1,
            deadline=timezone.now() + timedelta(days=1), status=False, completed_at=self._local_noon(0), user=self.user,)

        self.client.login(username='dashboard_stats_user', password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['today_done_count'], 2)
        self.assertEqual(response.context['last_7_days_done_counts'], [1, 0, 0, 0, 0, 1, 2])

    def test_dashboard_context_returns_zero_stats_without_completed_tasks(self):
        Task.objects.create(label='Only active task', description='Only active description', priority=1,
            deadline=timezone.now() + timedelta(days=1), status=False, user=self.user,)

        self.client.login(username='dashboard_stats_user', password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['today_done_count'], 0)
        self.assertEqual(response.context['last_7_days_done_counts'], [0, 0, 0, 0, 0, 0, 0])
