from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from datetime import timedelta
from .models import Task
from django.urls import reverse


class TaskModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='task_model_user', password='testpass123',)

    def test_task_creation_saves_main_fields(self):
        deadline = timezone.now() + timedelta(days=2)
        completed_at = timezone.now()

        task = Task.objects.create(label='Finish tests', description='Write tests for task', priority=3,
            deadline=deadline, status=True, completed_at=completed_at, user=self.user,)

        self.assertEqual(task.label, 'Finish tests')
        self.assertEqual(task.description, 'Write tests for task')
        self.assertEqual(task.priority, 3)
        self.assertEqual(task.deadline, deadline)
        self.assertTrue(task.status)
        self.assertEqual(task.completed_at, completed_at)
        self.assertEqual(task.user, self.user)

    def test_task_completed_at_is_empty_by_default(self):
        task = Task.objects.create(label='Default completed_at', description='', priority=1,
            deadline=timezone.now() + timedelta(days=1), user=self.user,)

        self.assertFalse(task.status)
        self.assertIsNone(task.completed_at)

    def test_task_string_representation_returns_label(self):
        task = Task.objects.create(label='Readable task title', description='Task description', priority=2,
            deadline=timezone.now() + timedelta(days=3), user=self.user,)

        self.assertEqual(str(task), 'Readable task title')


class TasksListViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tasks_owner', password='testpass123',)
        self.other_user = get_user_model().objects.create_user(username='tasks_other', password='testpass123',)

        self.own_task = Task.objects.create(label='Owner task', description='Owner description', priority=2,
            deadline=timezone.now() + timedelta(days=1), user=self.user,)
        self.other_task = Task.objects.create(label='Other task', description='Other description', priority=1,
            deadline=timezone.now() + timedelta(days=2), user=self.other_user,)

    def test_authenticated_user_can_open_tasks_list(self):
        self.client.login(username='tasks_owner', password='testpass123')

        response = self.client.get(reverse('tasks:tasks'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/tasks.html')

    def test_tasks_list_shows_only_current_user_tasks(self):
        self.client.login(username='tasks_owner', password='testpass123')

        response = self.client.get(reverse('tasks:tasks'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.own_task, response.context['task'])
        self.assertNotIn(self.other_task, response.context['task'])
        self.assertContains(response, 'Owner task')
        self.assertNotContains(response, 'Other task')
