from django.shortcuts import render
from tasks.models import Task
from .forms import TaskForm
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    form = TaskForm()
    task = Task.objects.filter(user=request.user)
    return render(request, 'tasks/tasks.html', {'form' : form, 'task' : task})

@login_required
def task(request, id):
    try:
        task = Task.objects.get(id=id, user=request.user)
    except Task.DoesNotExist:
        return HttpResponseNotFound('<h2>Task not found</h2>')
    return render(request, 'tasks/task.html', {'task' : task})