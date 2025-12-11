from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .decorators import assinatura_ativa_required
from billing.models import Subscription
from .llm_utils import gerar_conteudo
import openai


class GerarConteudoView(APIView):
    permission_classes = []

    def post(self, request):
        # Verifica assinatura ativa
        #assinatura = Subscription.objects.filter(user=request.user, #active=True).first()
        #if not assinatura:
            #return Response({"error": "Assinatura inativa"}, status=403)

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

            return Response({"resultado": resultado})

        except Exception as e:
            return Response({"error": str(e)}, status=500)
