from billing.models import Subscription
from billing.utils import get_valid_subscription
from rest_framework.response import Response 


def assinatura_ativa_required(func):
    def wrapper(self, request, *args, **kwargs):
        if not get_valid_subscription(request.user):
            return Response({'error': 'Assinatura inativa'}, status=403)
        return func(self, request, *args, **kwargs)
    return wrapper
