from django.shortcuts import render 


def dashboard_view(request):
    return render(request, 'dashboard.html')


def login_page(request):
    return render(request, 'login.html')


def register_page(request):
    return render(request, 'register.html')
