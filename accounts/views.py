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




MAX_BETA_USERS = 15

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")

            if not email or not password:
                return Response(
                    {'error': 'Email e senha são obrigatórios'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if User.objects.filter(username=email).exists():
                return Response(
                    {"error": "Usuário já existe"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # BLOQUEIO DO BETA
            total_beta_users = Subscription.objects.filter(
                status = 'trial'
            ).count()
            
            if total_beta_users >= MAX_BETA_USERS:
                return Response(
                    {
                        'error': "🚧 Beta fechado. As 15 vagas já foram preenchidas."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # 1. Criar usuário
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )

            # 2. Trial é sempre Basic
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
            },
            status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print("❌ ERRO REGISTER:", repr(e))
            return Response(
                {'error': 'Erro ao criar conta'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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