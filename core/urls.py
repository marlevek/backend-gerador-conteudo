from django.contrib import admin
from django.urls import path, include
from .views import dashboard_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("accounts.urls")),
    path("billing/", include("billing.urls")),
    path("api/", include("api.urls")),


    path("", dashboard_view, name="dashboard"),  # <-- ROTA PARA A RAIZ "/
]
