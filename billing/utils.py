from django.utils import timezone
from .models import MonthlyUsage


PLAN_CAPABILITIES = {
    "Basic": {
        "history": False,
        "export": False,
        "video_features": False,
        "max_requests_per_day": 20,
    },
    "Creator": {
        "history": True,
        "export": False,
        "video_features": True,
        "max_requests_per_day": 80,
    },
    "Elite": {
        "history": True,
        "export": True,
        "video_features": True,
        "max_requests_per_day": 9999,
    },
}


def get_or_create_monthly_usage(user):
    now = timezone.now()
    
    usage, created = MonthlyUsage.objects.get_or_create(
        user = user,
        year = now.year,
        month = now.month,
        defaults = {'used_posts': 0}
    )
    
    return usage

