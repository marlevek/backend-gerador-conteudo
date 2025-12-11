from django.urls import path 
from .views import webhook_pagamento 


urlpatterns = [
    path('webhook/', webhook_pagamento),
]