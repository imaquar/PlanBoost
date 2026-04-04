from django.shortcuts import render
from tasks.models import Task
from .forms import TaskForm
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

@login_required
def index(request):
    show_completed = request.GET.get('show') == 'completed'
    if show_completed:
        task = Task.objects.filter(user=request.user, status=True)
    else:
        task = Task.objects.filter(user=request.user, status=False)
    return render(request, 'tasks/tasks.html', {'task': task, 'show_completed': show_completed})

@login_required
def task(request, id):
    try:
        task = Task.objects.get(id=id, user=request.user)
    except Task.DoesNotExist:
        return HttpResponseNotFound('<h2>Task not found</h2>')
    return render(request, 'tasks/task.html', {'task' : task})

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

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task.label = form.cleaned_data['label']
            task.description = form.cleaned_data['description']
            task.deadline = form.cleaned_data['deadline']
            task.priority = form.cleaned_data['priority']
            task.save()
        return HttpResponseRedirect(f'/tasks/task/{id}/')
    else:
        form = TaskForm(model_to_dict(task))
        return render(request, 'tasks/edit.html', {'form': form, 'task': task})
    
@login_required
@require_POST
def delete(request, id):
    try:
        task = Task.objects.get(id=id, user=request.user)
    except Task.DoesNotExist:
        return HttpResponseNotFound('<h2>Task not found</h2>')
    task.delete()
    return HttpResponseRedirect('/tasks/')

@login_required
@require_POST
def toggle_status(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    is_done = 'status' in request.POST
    task.status = is_done
    task.completed_at = timezone.now() if is_done else None
    task.save(update_fields=['status', 'completed_at'])
    return redirect(request.POST.get('next') or 'tasks:tasks')