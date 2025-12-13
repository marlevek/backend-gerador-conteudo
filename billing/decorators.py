from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from billing.utils import PLAN_CAPABILITIES
from billing.models import Subscription


def require_capability(capability):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            sub = Subscription.objects.filter(user=request.user, active=True).first()
            if not sub or not sub.plan:
                return Response({"detail": "Assinatura inativa"}, status=status.HTTP_403_FORBIDDEN)

            caps = PLAN_CAPABILITIES.get(sub.plan.name, {})
            if not caps.get(capability):
                return Response(
                    {"detail": f"Recurso '{capability}' não disponível no seu plano"},
                    status=status.HTTP_403_FORBIDDEN
                )
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
