from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from tasks.models import Task
from notes.models import Note
from tasks.services import get_task_completion_stats

@login_required
def index(request):
    upcoming_tasks = (Task.objects.filter(user=request.user, status=False, deadline__gte=timezone.now(),).order_by('deadline')[:3])
    recent_notes = (Note.objects.filter(user=request.user).order_by('-created_at')[:3])
    stats = get_task_completion_stats(request.user)
    return TemplateResponse(request,'dashboard/dashboard.html', {'upcoming_tasks': upcoming_tasks,
        'recent_notes': recent_notes, 'today_done_count': stats['today_done_count'],
        'last_7_days_done_counts': stats['last_7_days_done_counts'],},)