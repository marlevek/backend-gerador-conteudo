from django.utils import timezone
from .models import MonthlyUsage
from django.utils.timezone import now
from .models import Subscription


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


def get_valid_subscription(user):
    now_time = now()

    # 1️⃣ Assinatura paga ativa (prioridade máxima)
    sub = (
        Subscription.objects
        .filter(
            user=user,
            active=True,
            status__in=["active", "approved"],
        )
        .order_by("-start_date")
        .first()
    )

    if sub:
        return sub

    # 2️⃣ Trial válido (Basic, pending ou trial)
    sub = (
        Subscription.objects
        .filter(
            user=user,
            status__in=["trial", "pending"],
            end_date__gte=now_time,
        )
        .order_by("-end_date")
        .first()
    )

    return sub
