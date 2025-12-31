from django.urls import path 
from .views import webhook_pagamento, criar_assinatura, minha_assinatura


urlpatterns = [
    path('assinar/', criar_assinatura, name='criar_assinatura'),
    path('webhook/mercadopago/', webhook_pagamento),  
    path('minha-assinatura/', minha_assinatura, name='minha_assinatura'),

]