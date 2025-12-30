from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from billing.models import Plan, Subscription
from django.utils.timezone import now
from datetime import timedelta



class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")

            if not email or not password:
                return Response(
                    {'error': 'Email e senha são obrigatórios'},
                    status=400
                )

            if User.objects.filter(username=email).exists():
                return Response(
                    {"error": "Usuário já existe"},
                    status=400
                )

            # 1. Criar usuário
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )

            # 2. Buscar plano BASIC (já seedado)
            basic_plan = Plan.objects.get(
                external_reference='basic_monthly'
            )

            # 3. Criar subscription de trial
            Subscription.objects.create(
                user=user,
                plan=basic_plan,
                status='trial',
                active=False,
                end_date=now() + timedelta(days=7),
            )

            # 4. Gerar JWT
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': "Usuário criado com sucesso",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })

        except Exception as e:
            print("❌ ERRO REGISTER:", repr(e))
            return Response(
                {'error': 'Erro ao criar conta'},
                status=500
            )

        

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email e senha são obrigatórios'},
                status = status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username = email, password = password)
        
        if not user:
            return Response(
                {'error': 'Credenciais Inválidas'},
                status = status.HTTP_401_UNAUTHORIZED
            )
            
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
        

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        refresh = request.data.get('refresh')
        
        if not refresh:
            return Response(
                {'error': 'Refresh token é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except TokenError:
            return Response(
                {'error': 'Token inválido ou já revogago'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'ok': True}, status=status.HTTP_200_OK)