from billing.models import Subscription 
from rest_framework.response import Response 


def assinatura_ativa_required(func):
    def wrapper(self, request):
        assinatura = Subscription.objects.filter(
            user = request.user,
            active = True
        ).first()
        
        if not assinatura:
            return Response({'error': 'Assinatura inativa'}, status=403)
        
        return func(self, request)
    
    return wrapper