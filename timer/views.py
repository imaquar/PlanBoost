from django.template.response import TemplateResponse

def index(request):
    return TemplateResponse(request, 'timer/timer.html')