from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .forms import NoteForm
from .models import Note


class NoteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='noteuser01', password='StrongPass123',)

    def test_note_creation_saves_basic_fields_and_user(self):
        note = Note.objects.create(label='My note title', text='My note text', user=self.user,)

        self.assertEqual(note.label, 'My note title')
        self.assertEqual(note.text, 'My note text')
        self.assertEqual(note.user, self.user)
        self.assertIsNotNone(note.created_at)

    def test_note_string_representation_returns_label(self):
        note = Note.objects.create(label='Some title', text='Some text', user=self.user,)

        self.assertEqual(str(note), 'Some title')


class NotesListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='notesowner', password='StrongPass123',)
        self.other_user = User.objects.create_user(username='othernotes', password='StrongPass123',)

    def test_authenticated_user_can_open_notes_list(self):
        self.client.login(username='notesowner', password='StrongPass123')

        response = self.client.get(reverse('notes:notes'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/notes.html')

    def test_notes_list_contains_only_current_user_notes(self):
        own_note = Note.objects.create(label='Owner note', text='Owner text', user=self.user,)
        Note.objects.create(label='Other note', text='Other text', user=self.other_user,)
        self.client.login(username='notesowner', password='StrongPass123')

        response = self.client.get(reverse('notes:notes'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(own_note, response.context['note'])
        self.assertContains(response, 'Owner note')
        self.assertNotContains(response, 'Other note')


class NoteCreationFormAndViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='notecreator', password='StrongPass123',)

    def test_note_form_is_valid_with_correct_data(self):
        form = NoteForm(
            data={'label': 'Created title', 'text': 'Created text',}
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_note_form_is_invalid_without_required_label(self):
        form = NoteForm(
            data={'label': '', 'text': 'Created text',}
        )

        self.assertFalse(form.is_valid())
        self.assertIn('label', form.errors)

    def test_create_note_view_saves_note_for_current_user(self):
        self.client.login(username='notecreator', password='StrongPass123')

        response = self.client.post(
            reverse('notes:create'),
            data={'label': 'View created title', 'text': 'View created text',},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/notes/')

        created_note = Note.objects.get(label='View created title')
        self.assertEqual(created_note.text, 'View created text')
        self.assertEqual(created_note.user, self.user)
