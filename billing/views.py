from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Plan, Subscription
from billing.models import Subscription
from billing.utils import get_or_create_monthly_usage
import json 
from django.http import HttpResponse 
from django.utils.dateparse import parse_date 
from django.utils.timezone import now
from datetime import timedelta


@api_view(['POST'])
@permission_classes([AllowAny])
def webhook_pagamento(request):
    data = request.data

    email = data.get("buyer_email")
    status = data.get("status")
    plan_id = data.get("plan_id")

    user = User.objects.filter(username=email).first()
    
    if not user:
        return Response({"error": "Usuário não encontrado"}, status=404)

    plan = Plan.objects.filter(external_reference=plan_id).first()
    if not plan:
        return Response({"error": "Plano não encontrado"}, status=404)
    
    # Desmarcar para produção:
    if status not in ['approved', 'paid', 'active']:
        return Response({'message': "Pagamento não aprovado"}, status=200)

    # Deixar comentado para produção:
    '''if status in ['approved', 'paid', 'active', 'pending']:
        sub.activate()
    else:
        sub.deactivated(status)'''
        

    # Criar ou atualizar assinatura
    sub, created = Subscription.objects.get_or_create(
    user=user,
    defaults={
        "plan": plan,
        "active": True,
        "start_date": now(),
        "end_date": now() + timedelta(days=30),
    }
)
    # Se já existia, atualiza plano
    if not created:
        sub.plan = plan
        sub.active = True
        sub.start_date = now()
        sub.end_date = now() + timedelta(days=30)
        sub.save()
    
    # Garantir Monthly usage
    get_or_create_monthly_usage(user)

    return Response({"message": "OK"}, status=200)


