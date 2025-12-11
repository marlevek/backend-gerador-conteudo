from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Plan, Subscription

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

    sub, _ = Subscription.objects.get_or_create(user=user, plan=plan)

    if status in ["approved", "paid", "active"]:
        sub.activate()
    else:
        sub.deactivate(status)

    return Response({"message": "OK"}, status=200)


