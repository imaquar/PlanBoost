from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    label = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    status = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    PRIORITY_CHOICES = [(1, "Low"), (2, "Medium"), (3, "High"),]
    priority = models.IntegerField(choices=PRIORITY_CHOICES)

    class Meta:
        ordering = ['deadline']
        indexes = [
            models.Index(fields=['deadline']),
        ]

    def __str__(self):
        return self.label[:50]
