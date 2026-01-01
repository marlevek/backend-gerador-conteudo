from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .decorators import assinatura_ativa_required
from billing.models import Subscription, ContentHistory, Plan
from billing.utils import PLAN_CAPABILITIES, get_or_create_monthly_usage, get_valid_subscription
from .llm_utils import gerar_conteudo
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
import csv
from django.http import HttpResponse
from billing.models import ContentHistory
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import openai
from datetime import timedelta


class GerarConteudoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Verifica assinatura ativa
        # assinatura = Subscription.objects.filter(user=request.user, #active=True).first()
        # if not assinatura:
        # return Response({"error": "Assinatura inativa"}, status=403)

        user = request.user
        data = request.data

        # Verificar Assinatura
        valid_subscription = get_valid_subscription(user)

        if not valid_subscription:
            return Response(
                {'error': 'Assinatura inativa ou inexistente'},
                status=403
            )

        plan = valid_subscription.plan

        PLATAFORMAS_VIDEO = [
            'Instagram Reels',
            'Youtube Short',
            'Tiktok (video curto)',
        ]

        # Bloqueio de vídeo curto para plano Basic
        if plan.name == 'Basic' and data.get('plataforma') in PLATAFORMAS_VIDEO:
            return Response(
                {
                    'error': 'Seu plano não inclui geração de roteiros para vídeos curtos.',
                    'plan': plan.name,
                    'upgrade_required': True,
                },
                status=403
            )

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
            return Response(
                {"error": f"Erro ao gerar conteúdo:{ str(e)}"}, 
                status=500
                )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user

    subscription = (
        Subscription.objects
        .filter(user=user)
        .select_related('plan')
        .order_by('-start_date')
        .first()
    )

    valid_subscription = get_valid_subscription(user)
    usage = get_or_create_monthly_usage(user)

    is_trial = (
        subscription
        and subscription.status == "trial"
        and subscription.end_date
        and subscription.end_date >= now()
    )
    
    if valid_subscription and valid_subscription.plan:
         plan_name = valid_subscription.plan.name
         capabilities = PLAN_CAPABILITIES.get(plan_name, {})
         limit = valid_subscription.plan.max_posts
    else:
        plan_name = None
        capabilities = {} 
        limit = 0

    return Response({
        "email": user.email,
        "is_authenticated": True,

        # acesso técnico (trial OU pago)
        "subscription_active": bool(valid_subscription),

        # estado da assinatura
        "subscription_status": subscription.status if subscription else None,
        "trial_ends_at": subscription.end_date if is_trial else None,

        # plano real
        "plan": plan_name,
        "is_trial": is_trial,

        # capacidades
        "capabilities": capabilities,

        # uso
        "used": usage.used_posts,
        "limit": limit,
    })



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def usage_me(request):
    user = request.user
    
    subscription = get_valid_subscription(request.user)

    if not subscription:
        return Response(
            {"error": "Assinatura inativa ou trial expirado"},
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
    plataforma = request.GET.get('plataforma')

    subscription =(
        Subscription.objects.filter(user=user).select_related('plan').order_by('-start_date').first()
        )

    if not subscription:
        return Response({"error": "Assinatura inativa"}, status=403)
    
    # trial e basic não tem histórico
    if subscription.status == 'trial' or subscription.plan.name == 'Basic':
        return Response(
            {'error': 'Histórico disponível apenas a partir do plano creator'},
            status=403
        )

    qs = ContentHistory.objects.filter(user=user)

    # Filtro por plataforma
    if plataforma:
        qs = qs.filter(plataforma=plataforma)

    # Creator - últimos 30 dias
    if subscription.plan.name == 'Creator':
        qs = qs.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        )
    data = [
        {
            "id": h.id,
            "tema": h.tema,
            "plataforma": h.plataforma,
            "conteudo": h.conteudo,
            "created_at": h.created_at.strftime("%d/%m/%Y %H:%M"),
            "plan": h.plan.name if h.plan else "",
        }
        for h in qs.order_by('-created_at')[:100]
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_historico_csv(request):
    user = request.user

    subscription = Subscription.objects.filter(
        user=user, active=True
    ).select_related("plan").first()

    if not subscription or subscription.plan.name != "Elite":
        return HttpResponse("Plano não permite exportação", status=403)

    queryset = ContentHistory.objects.filter(user=user)

    # Creator = últimos 30 dias | Elite = ilimitado
    if subscription.plan.name == "Creator":
        queryset = queryset.filter(
            created_at__gte=now() - timedelta(days=30)
        )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        'attachment; filename="historico_conteudos.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        "Data",
        "Tema",
        "Plataforma",
        "Tom",
        "Nicho",
        "Conteúdo",
        "Plano",
    ])

    for item in queryset:
        writer.writerow([
            item.created_at.strftime("%d/%m/%Y %H:%M"),
            item.tema,
            item.plataforma,
            item.tom,
            item.nicho,
            item.conteudo,
            item.plan.name if item.plan else "",
        ])

    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_historico_pdf(request):
    user = request.user

    content_id = request.GET.get("id")

    qs = ContentHistory.objects.filter(user=request.user)

    if content_id:
        qs = qs.filter(id=content_id)

    # Verifica assinatura ativa
    subscription = Subscription.objects.filter(
        user=user,
        active=True
    ).select_related("plan").first()

    if not subscription or subscription.plan.name != "Elite":
        return HttpResponse(
            "Plano não permite exportação em PDF",
            status=403
        )

    queryset = qs

    # Creator = 30 dias | Elite = ilimitado
    if subscription.plan.name == "Creator":
        queryset = queryset.filter(
            created_at__gte=now() - timedelta(days=30)
        )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        'attachment; filename="historico_conteudos.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 40

    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, "Histórico de Conteúdos Gerados")
    y -= 30

    p.setFont("Helvetica", 9)

    for item in queryset.order_by("-created_at"):
        if y < 80:
            p.showPage()
            p.setFont("Helvetica", 9)
            y = height - 40

        p.drawString(
            40, y,
            f"{item.created_at.strftime('%d/%m/%Y %H:%M')} | {item.plataforma}"
        )
        y -= 14

        p.setFont("Helvetica-Bold", 10)
        p.drawString(40, y, f"Tema: {item.tema}")
        y -= 14

        p.setFont("Helvetica", 9)

        texto = item.conteudo.split("\n")
        for linha in texto:
            if y < 60:
                p.showPage()
                p.setFont("Helvetica", 9)
                y = height - 40
            p.drawString(50, y, linha[:110])
            y -= 12

        y -= 20

    p.showPage()
    p.save()

    return response
