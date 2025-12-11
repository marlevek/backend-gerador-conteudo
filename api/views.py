from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .decorators import assinatura_ativa_required
import openai


class GerarConteudoView(APIView):
    permission_classes = [IsAuthenticated]
    
    @assinatura_ativa_required
    def post(self, request):
        prompt = request.data.get('prompt')
        
        resposta = openai.chat.completions.create(
            model = 'gpt-4o-mini',
            messages = [{'role': 'user', 'content': prompt}]
        )
        
        return Response({
            'resultado': resposta.choices[0].message['content']
        })
