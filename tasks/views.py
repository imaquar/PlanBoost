from django.shortcuts import render
from tasks.models import Task
from .forms import TaskForm
from django.http import HttpResponseRedirect, HttpResponseNotFound, JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from urllib.parse import urlparse, urlencode
from django.urls import reverse
from .services import get_task_completion_stats


def _normalize_tasks_next(next_url):
    text = str(next_url or '').strip()
    if not text:
        return '/tasks/'

    parsed = urlparse(text)
    path = parsed.path or ''
    normalized_path = path if path.endswith('/') else path + '/'

    if normalized_path != '/tasks/':
        return '/tasks/'

    if parsed.query:
        return '/tasks/?' + parsed.query
    return '/tasks/'

@login_required
def index(request):
    show_completed = request.GET.get('show') == 'completed'
    sort = request.GET.get('sort', 'deadline')
    qs = Task.objects.filter(user=request.user, status=show_completed)
    if sort == 'priority':
        qs = qs.order_by('-priority', 'deadline')
    else:
        qs = qs.order_by('deadline')
    return render(request, 'tasks/tasks.html', {'task': qs, 'show_completed': show_completed, 'sort': sort})

@login_required
def task(request, id):
    try:
        task = Task.objects.get(id=id, user=request.user)
    except Task.DoesNotExist:
        return HttpResponseNotFound('<h2>Task not found</h2>')

    next_url = _normalize_tasks_next(request.GET.get('next', '').strip())
    if next_url == '/tasks/':
        referer = request.META.get('HTTP_REFERER', '').strip()
        if referer:
            next_url = _normalize_tasks_next(referer)

    return render(request, 'tasks/task.html', {'task' : task, 'next': next_url})

@login_required
def create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = Task()
            task.label = form.cleaned_data['label']
            task.description = form.cleaned_data['description']
            task.deadline = form.cleaned_data['deadline']
            task.priority = form.cleaned_data['priority']
            task.status = False
            task.user = request.user
            task.save()
            return HttpResponseRedirect('/tasks/')
    else:
        form = TaskForm()

    return render(request, 'tasks/create.html', {'form': form})

@login_required
def edit(request, id):
    try:
        task = Task.objects.get(id=id, user=request.user)
    except Task.DoesNotExist:
        return HttpResponseNotFound('<h2>Task not found</h2>')

    next_url = _normalize_tasks_next(request.GET.get('next', '') or request.POST.get('next', ''))

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task.label = form.cleaned_data['label']
            task.description = form.cleaned_data['description']
            task.deadline = form.cleaned_data['deadline']
            task.priority = form.cleaned_data['priority']
            task.save()
        task_url = reverse('tasks:task', args=[id])
        return HttpResponseRedirect(f'{task_url}?{urlencode({"next": next_url})}')
    else:
        form = TaskForm(model_to_dict(task))
        return render(request, 'tasks/edit.html', {'form': form, 'task': task, 'next': next_url})
    
@login_required
@require_POST
def delete(request, id):
    try:
        task = Task.objects.get(id=id, user=request.user)
    except Task.DoesNotExist:
        return HttpResponseNotFound('<h2>Task not found</h2>')
    task.delete()
    return redirect(request.POST.get('next') or 'tasks:tasks')

@login_required
@require_POST
def toggle_status_ajax(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    raw_status = request.POST.get('status')
    is_done = str(raw_status).lower() in ('1', 'true', 'on', 'yes')

    task.status = is_done
    task.completed_at = timezone.now() if is_done else None
    task.save(update_fields=['status', 'completed_at'])

    return JsonResponse({
        'ok': True,
        'id': task.id,
        'status': task.status,
        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
    })


def _tasks_payload(user, sort, show_completed):
    qs = Task.objects.filter(user=user, status=show_completed)
    if sort == 'priority':
        qs = qs.order_by('-priority', 'deadline')
    else:
        sort = 'deadline'
        qs = qs.order_by('deadline')

    tasks = []
    for task in qs:
        deadline_display = ''
        if task.deadline:
            deadline_value = timezone.localtime(task.deadline) if timezone.is_aware(task.deadline) else task.deadline
            deadline_display = deadline_value.strftime('%d.%m.%y %H:%M')

        completed_display = ''
        if task.completed_at:
            completed_value = timezone.localtime(task.completed_at) if timezone.is_aware(task.completed_at) else task.completed_at
            completed_display = completed_value.strftime('%d.%m.%y %H:%M')

        tasks.append({
            'id': task.id,
            'label': task.label,
            'status': task.status,
            'priority': task.priority,
            'priority_display': task.get_priority_display(),
            'deadline': task.deadline.isoformat() if task.deadline else None,
            'deadline_display': deadline_display,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'completed_at_display': completed_display,
        })

    return {
        'ok': True,
        'sort': sort,
        'show_completed': show_completed,
        'tasks': tasks,
    }


@login_required
@require_GET
def tasks_list_ajax(request):
    sort = request.GET.get('sort', 'deadline')
    show_completed = request.GET.get('show') == 'completed'
    return JsonResponse(_tasks_payload(request.user, sort, show_completed))


@login_required
@require_GET
def tasks_filter_ajax(request):
    show_completed = request.GET.get('show') == 'completed'
    sort = request.GET.get('sort', 'deadline')
    return JsonResponse(_tasks_payload(request.user, sort, show_completed))

@login_required
@require_GET
def stats(request):
    data = get_task_completion_stats(request.user)
    return JsonResponse(data)
