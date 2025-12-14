from django.urls import path
from .views import GerarConteudoView, me, usage_me, historico, export_historico_csv, export_historico_pdf


urlpatterns = [
    path("gerar/", GerarConteudoView.as_view()),
    path('me/', me),
    path('usage/', usage_me),
    path('historico/', historico),
    path('historico/export/csv/', export_historico_csv),
    path('historico/export/pdf/', export_historico_pdf, name='export_historico_pdf'),

]
