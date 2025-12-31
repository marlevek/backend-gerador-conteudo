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
    """
    Retorna a assinatura válida do usuário:
    - trial ainda válido
    - ou assinatura ativa
    Caso contrário, retorna None.
    """
    sub = (
        Subscription.objects
        .filter(user=user)
        .order_by("-start_date")
        .first()
    )

    if not sub:
        return None

    # Trial válido
    if sub.status == "trial" and sub.end_date and sub.end_date >= now():
        sub.active = False 
        sub.save(update_fields=['active'])
        return None

    # Assinatura ativa
    if sub.status == "active" and sub.active:
        return sub

    return None