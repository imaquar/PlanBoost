from django.contrib import admin
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('label', 'user', 'created_at')
    search_fields = ('label', 'text', 'user__username')
    list_filter = ('created_at', 'user')
    ordering = ('-created_at',)
