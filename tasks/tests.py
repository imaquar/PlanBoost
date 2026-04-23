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


class TaskCreationFormAndViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='taskcreator', password='testpass123',)

    def test_task_form_is_valid_with_correct_data(self):
        from .forms import TaskForm
        deadline_input = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')

        form = TaskForm(data={'label': 'Created task', 'description': 'Created description',
            'deadline': deadline_input, 'priority': '2',})

        self.assertTrue(form.is_valid(), form.errors)

    def test_task_form_is_invalid_without_required_label(self):
        from .forms import TaskForm
        deadline_input = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')

        form = TaskForm(data={'label': '', 'description': 'Created description',
            'deadline': deadline_input, 'priority': '2',})

        self.assertFalse(form.is_valid())
        self.assertIn('label', form.errors)

    def test_create_task_view_saves_task_for_current_user(self):
        self.client.login(username='taskcreator', password='testpass123')
        deadline_input = (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M')

        response = self.client.post(reverse('tasks:create'), data={'label': 'View created task',
            'description': 'View created description', 'deadline': deadline_input, 'priority': '3',})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/tasks/')

        created_task = Task.objects.get(label='View created task', user=self.user)
        self.assertEqual(created_task.description, 'View created description')
        self.assertEqual(created_task.priority, 3)
        self.assertFalse(created_task.status)
        self.assertEqual(created_task.user, self.user)
        self.assertIsNotNone(created_task.deadline)


class TaskEditingTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username='taskowner', password='testpass123',)
        self.other_user = get_user_model().objects.create_user(username='taskintruder', password='testpass123',)
        self.task = Task.objects.create(label='Original task', description='Original description', priority=2,
            deadline=timezone.now() + timedelta(days=1), user=self.owner,)

    def test_owner_can_edit_own_task(self):
        self.client.login(username='taskowner', password='testpass123')
        new_deadline = (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M')

        response = self.client.post(reverse('tasks:edit', args=[self.task.id]), data={
            'label': 'Updated task', 'description': 'Updated description', 'deadline': new_deadline, 'priority': '1',})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/tasks/task/{self.task.id}/')

        self.task.refresh_from_db()
        self.assertEqual(self.task.label, 'Updated task')
        self.assertEqual(self.task.description, 'Updated description')
        self.assertEqual(self.task.priority, 1)

    def test_other_user_cannot_edit_foreign_task(self):
        self.client.login(username='taskintruder', password='testpass123')
        new_deadline = (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M')

        response = self.client.post(reverse('tasks:edit', args=[self.task.id]), data={
            'label': 'Hacked task', 'description': 'Hacked description', 'deadline': new_deadline, 'priority': '3',})

        self.assertEqual(response.status_code, 404)

        self.task.refresh_from_db()
        self.assertEqual(self.task.label, 'Original task')
        self.assertEqual(self.task.description, 'Original description')
        self.assertEqual(self.task.priority, 2)


class TaskDeletionTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username='taskdeleteowner', password='testpass123',)
        self.other_user = get_user_model().objects.create_user(username='taskdeleteintruder', password='testpass123',)
        self.task = Task.objects.create(label='Delete task', description='Delete description', priority=2,
            deadline=timezone.now() + timedelta(days=2), user=self.owner,)

    def test_owner_can_delete_own_task(self):
        self.client.login(username='taskdeleteowner', password='testpass123')

        response = self.client.post(reverse('tasks:delete', args=[self.task.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('tasks:tasks'))
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_other_user_cannot_delete_foreign_task(self):
        self.client.login(username='taskdeleteintruder', password='testpass123')

        response = self.client.post(reverse('tasks:delete', args=[self.task.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(id=self.task.id).exists())
