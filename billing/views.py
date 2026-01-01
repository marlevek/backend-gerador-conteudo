from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
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
from .models import Plan, Subscription



# Criar Assinatura/Planos
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_assinatura(request):
    plan_id = request.data.get("plan_id")

    if not plan_id:
        return Response({"error": "Plano não informado"}, status=400)

    plan = Plan.objects.filter(id=plan_id, active=True).first()

    if not plan:
        return Response({"error": "Plano inválido"}, status=404)

    checkout_url = (
        "https://www.mercadopago.com.br/subscriptions/checkout"
        f"?preapproval_plan_id={plan.external_reference}"
        "&back_url=https://app.gerador.codertec.com.br/assinatura/sucesso/"
        "&failure_url=https://app.gerador.codertec.com.br/assinatura/falha/"
    )

    return Response({
        "checkout_url": checkout_url
    })



@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def webhook_pagamento(request):
    data = request.data
    
    status_mp = data.get('status') or data.get('action')

    # Tolerância ao payload do MP
    payer_email = (
        data.get("payer_email")
        or data.get("buyer_email")
        or data.get("payer", {}).get("email")
    )
    plan_id = (
        data.get("preapproval_plan_id")
        or data.get("plan_id")
    )
    mp_subscription_id = data.get("id") or data.get("preapproval_id")

    if not payer_email or not plan_id:
        return Response({"error": "Payload inválido"}, status=400)

    user = User.objects.filter(email=payer_email).first()
    if not user:
        return Response({"error": "Usuário não encontrado"}, status=404)

    plan = Plan.objects.filter(external_reference=plan_id).first()
    if not plan:
        return Response({"error": "Plano não encontrado"}, status=404)
    
    # Regra de ouro: 1 subscription por usuário
    sub, created = Subscription.objects.get_or_create(
        user = user,
        defaults={
            'plan': plan,
            'status': 'pending',
            'active': False,
        }
    )
    
    # Atualiza dados
    sub.plan = plan 
    sub.mercado_pago_subscription_id = mp_subscription_id 
    sub.last_payment_status = status_mp
    
    if status_mp in ["authorized", "approved", "paid", "active"]:
        sub.status = 'active'
        sub.active = True 
        sub.start_date = now()
        
        if plan.recurrence == 'yearly':
            sub.end_date = now() + timedelta(days=365)
        else:
            sub.end_date = now() + timedelta(days=30)
    
    else:
        sub.active = False 
        sub.status = 'pending'
        
    sub.save()
    
    return Response({'message': 'Webhook processado com sucesso.'}, status=200)
        
    
    



# Pg de redirecionamento após pagamento
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def minha_assinatura(request):
    sub = (
        Subscription.objects.filter(user=request.user).order_by('-start_date').first()
    )
    
    if not sub:
        return Response({'has_subscription': False})
    
    return Response({
        'has_subscription': True,
        'status': sub.status,
        'active': sub.active,
        'plan': sub.plan.name if sub.plan else None,
        'end_date': sub.end_date,
    })