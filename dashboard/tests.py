from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from datetime import timedelta
from django.utils import timezone
from notes.models import Note


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
