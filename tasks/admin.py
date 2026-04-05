from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('label', 'user', 'deadline')
    search_fields = ('label', 'user__username')
    list_filter = ('deadline', 'priority', 'status')
    ordering = ('deadline',)
