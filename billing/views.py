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

    # Tolerância ao payload do MP
    status = data.get("status") or data.get("action")
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

    sub, created = Subscription.objects.get_or_create(user=user)
    sub.plan = plan
    sub.mercado_pago_subscription_id = mp_subscription_id

    # Estados válidos do Mercado Pago
    if status in ['authorized', 'approved', 'paid', 'active']:
        sub.active = True
        sub.last_payment_status = status
        sub.start_date = now()

        # Calcular recorrência corretamente
        if plan.recurrence == 'yearly':
            sub.end_date = now() + timedelta(days=365)
        else:
            sub.end_date = now() + timedelta(days=30)

    else:
        sub.active = False
        sub.last_payment_status = status

    sub.save()

    # Garantir controle de uso mensal
    get_or_create_monthly_usage(user)

    return Response({"message": "Webhook processado com sucesso"}, status=200)