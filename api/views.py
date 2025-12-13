from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .decorators import assinatura_ativa_required
from billing.models import Subscription, ContentHistory
from billing.utils import PLAN_CAPABILITIES, get_or_create_monthly_usage
from .llm_utils import gerar_conteudo
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from datetime import timedelta
import openai


class GerarConteudoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Verifica assinatura ativa
        # assinatura = Subscription.objects.filter(user=request.user, #active=True).first()
        # if not assinatura:
            # return Response({"error": "Assinatura inativa"}, status=403)

        user = request.user

        # Verificar Assinatura
        subscription = Subscription.objects.filter(
            user=user,
            active=True,
        ).select_related('plan').first()

        if not subscription:
            return Response(
                {'error': 'Assinatura inativa ou inexistente'},
                status=403
            )

        plan = subscription.plan

        # buscar uso mensal
        usage = get_or_create_monthly_usage(user)

        # Bloquer se atingiu limite
        if usage.used_posts >= plan.max_posts:
            return Response(
                {
                    'error': 'Limite mensal de conteúdos atingido',
                    'plan': plan.name,
                    'limit': plan.max_posts,
                    'used': usage.used_posts,
                },
                status=429
            )

        data = request.data

        try:
            resultado = gerar_conteudo(
                modelo=data.get("modelo", "gpt-4o-mini"),
                temperatura=float(data.get("temperature", 0.7)),
                tema=data["tema"],
                plataforma=data["plataforma"],
                tom=data["tom"],
                tamanho=data["tamanho"],
                publico=data["publico"],
                incluir_cta=data["cta"],
                incluir_hashtags=data["hashtags"],
                palavras_chave=data.get("palavras_chave", ""),
                nicho=data.get("nicho", ""),
                incluir_sugestoes_imagens=data["sugestoes_imagens"],
            )

            # ✅ SALVAR HISTÓRICO
            ContentHistory.objects.create(
                user=user,
                plan=plan,
                tema=data.get("tema"),
                plataforma=data.get("plataforma"),
                tom=data.get("tom"),
                nicho=data.get("nicho", ""),
                conteudo=resultado,
            )

            with transaction.atomic():
                usage = get_or_create_monthly_usage(user)
                usage.used_posts = F('used_posts') + 1
                usage.save(update_fields=['used_posts'])
                usage.refresh_from_db()

            return Response(
                {"resultado": resultado,
                 'plan': plan.name,
                 'limit': plan.max_posts,
                 'used': usage.used_posts
                 })

        except Exception as e:
            return Response({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    
    subscription = Subscription.objects.filter(
        user = user,
        active = True
    ).first()
    
    plan_name = subscription.plan.name if subscription and subscription.plan else None
    capabilities = PLAN_CAPABILITIES.get(plan_name, {})
    
    return Response({
        'email': user.email,
        'is_authenticated': True,
        'subscription_active': bool(subscription),
        'plan': plan_name,
        'capabilities': capabilities,
    })
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def usage_me(request):
    user = request.user

    subscription = Subscription.objects.filter(
        user=user,
        active=True
    ).select_related("plan").first()

    if not subscription:
        return Response(
            {"error": "Assinatura inativa"},
            status=403
        )

    usage = get_or_create_monthly_usage(user)

    return Response({
        "plan": subscription.plan.name,
        "limit": subscription.plan.max_posts,
        "used": usage.used_posts,
    })
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def historico(request):
    user = request.user

    subscription = Subscription.objects.filter(
        user=user,
        active=True
    ).select_related("plan").first()

    if not subscription:
        return Response({"error": "Assinatura inativa"}, status=403)

    plan = subscription.plan

    qs = ContentHistory.objects.filter(user=user)

    # Regras por plano
    if plan.name == "Creator":
        limite_data = timezone.now() - timedelta(days=30)
        qs = qs.filter(created_at__gte=limite_data)

    elif plan.name == "Basic":
        return Response(
            {"error": "Histórico indisponível neste plano"},
            status=403
        )

    # Elite = ilimitado

    data = [
        {
            "id": h.id,
            "tema": h.tema,
            "plataforma": h.plataforma,
            "conteudo": h.conteudo,
            "created_at": h.created_at.strftime("%d/%m/%Y %H:%M"),
        }
        for h in qs[:100]
    ]

    return Response(data)
