from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from .models import Task

def get_task_completion_stats(user):
    today = timezone.localdate()
    start_day = today - timedelta(days=6)

    qs = (Task.objects.filter(user=user, status=True, completed_at__date__gte=start_day, 
                              completed_at__date__lte=today,).annotate(day=TruncDate("completed_at"))
                              .values("day").annotate(count=Count("id")))

    counts_by_day = {row["day"]: row["count"] for row in qs}

    last_7_days_done_counts = []
    for i in range(7):
        day = start_day + timedelta(days=i)
        last_7_days_done_counts.append(counts_by_day.get(day, 0))

    return {"today_done_count": counts_by_day.get(today, 0), "last_7_days_done_counts": last_7_days_done_counts,}
