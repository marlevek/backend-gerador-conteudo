from django.contrib import admin
from .models import Subscription, Plan, MonthlyUsage, ContentHistory


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'plan',
        'active',
        'start_date',
        'end_date',
        'last_payment_status',
    )
    
    list_filter = ('active', 'plan')
    search_fields = ('user__username', 'user__email')
    

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'external_reference')


@admin.register(MonthlyUsage)
class MonthlyUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'year', 'used_posts')
    list_filter = ('user', 'month')
    search_fields = ('user__username', 'user__email')
    

@admin.register(ContentHistory)
class ContentHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "tema",
        "plataforma",
        "created_at",
    )
    list_filter = ("plan", "plataforma", "created_at")
    search_fields = ("tema", "conteudo", "user__email")
    ordering = ("-created_at",)