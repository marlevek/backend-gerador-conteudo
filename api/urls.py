from django.urls import path
from .views import GerarConteudoView, me, usage_me, historico


urlpatterns = [
    path("gerar/", GerarConteudoView.as_view()),
    path('me/', me),
    path('usage/', usage_me),
    path('historico/', historico),
]
