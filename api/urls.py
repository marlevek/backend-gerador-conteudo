from django.urls import path
from .views import GerarConteudoView

urlpatterns = [
    path("gerar/", GerarConteudoView.as_view()),
]
