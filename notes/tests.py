from django.test import TestCase
from django.contrib.auth.models import User

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
