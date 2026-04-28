from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.utils import timezone
from tasks.models import Task
from notes.models import Note
from tasks.services import get_task_completion_stats

def _dashboard_payload(user):
    upcoming_tasks_qs = Task.objects.filter(user=user, status=False, deadline__gte=timezone.now()).order_by('deadline')[:3]
    recent_notes_qs = Note.objects.filter(user=user).order_by('-created_at')[:3]
    stats = get_task_completion_stats(user)

    upcoming_tasks = []
    for task in upcoming_tasks_qs:
        deadline_value = timezone.localtime(task.deadline) if timezone.is_aware(task.deadline) else task.deadline
        upcoming_tasks.append({
            'id': task.id,
            'label': task.label,
            'deadline': task.deadline.isoformat() if task.deadline else None,
            'deadline_display': deadline_value.strftime('%d.%m.%y %H:%M') if deadline_value else '',
            'priority': task.priority,
            'priority_display': task.get_priority_display(),
        })

    recent_notes = []
    for note in recent_notes_qs:
        created_value = timezone.localtime(note.created_at) if timezone.is_aware(note.created_at) else note.created_at
        recent_notes.append({
            'id': note.id,
            'label': note.label,
            'created_at': note.created_at.isoformat() if note.created_at else None,
            'created_at_display': created_value.strftime('%d.%m.%y %H:%M') if created_value else '',
        })

    return {
        'today': stats['today_done_count'],
        'last7': stats['last_7_days_done_counts'],
        'today_done_count': stats['today_done_count'],
        'last_7_days_done_counts': stats['last_7_days_done_counts'],
        'upcoming_tasks': upcoming_tasks,
        'recent_notes': recent_notes,
    }


@login_required
def index(request):
    data = _dashboard_payload(request.user)
    return TemplateResponse(request, 'dashboard/dashboard.html', data)


@login_required
@require_GET
def stats_ajax(request):
    return JsonResponse(_dashboard_payload(request.user))