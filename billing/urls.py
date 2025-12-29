from django.urls import path 
from .views import webhook_pagamento 


urlpatterns = [
    path('webhook/mercadopago/', webhook_pagamento),

]