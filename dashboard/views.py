from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from tasks.models import Task

@login_required
def index(request):
    upcoming_tasks = (Task.objects.filter(user=request.user, status=False, deadline__gte=timezone.now(),).order_by('deadline')[:3])
    return TemplateResponse(request,'dashboard/dashboard.html', {'upcoming_tasks': upcoming_tasks},)