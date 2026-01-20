from django.template.response import TemplateResponse

def index(request):
    return TemplateResponse(request, 'dashboard/dashboard.html')

def notes(request):
    return TemplateResponse(request, 'notes/notes.html')

def tasks(request):
    return TemplateResponse(request, 'tasks/tasks.html')

def timer(request):
    return TemplateResponse(request, 'timer/timer.html')