from django.shortcuts import render 
from django.contrib.auth.decorators import login_required


def dashboard_view(request):
    return render(request, 'dashboard.html')


def login_page(request):
    return render(request, 'login.html')


def register_page(request):
    return render(request, 'register.html')


# Sucesso Assinatura
@login_required
def assinatura_sucesso(request):
    return render(request, 'assinatura_sucesso.html')


# Falha Assinatura
@login_required
def assinatura_falha(request):
    return render(request, 'assinatura_falha.html')