from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone


class Plan(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    external_reference = models.CharField(
        max_length=150,
        unique=True,
        help_text='ID do plano no Mercado Pago'
    )

    # Controle de uso
    max_posts = models.IntegerField(
        default=100,
        help_text='Quantidade máxima de conteúdos gerados por período'
    )

    has_ai = models.BooleanField(
        default=True,
        help_text='Define se o plano tem acesso às funções de IA'
    )

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    recurrence = models.CharField(
        max_length=20,
        choices=(
            ('monthly', 'Mensal'),
            ('yearly', 'Anual'),
        ),
        default='monthly'
    )

    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATUS_CHOICES = (
        ('trial', 'Trial'),
        ('active', 'Ativa'),
        ('past_due', 'Pagamento atrasado'),
        ('canceled', 'Cancelada'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(
        Plan, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='trial',
    )

    active = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    last_payment_status = models.CharField(max_length=50, default="pending")
    mercado_pago_subscription_id = models.CharField(
        max_length=120,
        unique=True,
        null=True,
        blank=True,
    )
    mercado_pago_payment_id = models.CharField(
        max_length=120,
        null=True,
        blank=True,
    )

    def activate(self):
        self.status = 'active'
        self.active = True
        self.end_date = timezone.now() + timedelta(days=30)
        self.last_payment_status = "paid"
        self.save()

    def deactivate(self, status):
        self.status = 'canceled'
        self.active = False
        self.last_payment_status = status
        self.save()
        
    @property
    def is_trial(self):
        return self.status == "trial"


    @property
    def is_active(self):
        return self.status == "active" and self.end_date and self.end_date > timezone.now()


    def __str__(self):
        return f"{self.user} - {self.plan} - Ativa: {self.active}"



class MonthlyUsage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()

    used_posts = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'year', 'month')

    def __str__(self):
        return f"{self.user} - {self.month}/{self.year}"


class ContentHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='content_history'
    )

    plan = models.ForeignKey(
        'billing.Plan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Dados do conteúdo
    tema = models.CharField(max_length=255)
    plataforma = models.CharField(max_length=100)
    tom = models.CharField(max_length=50)
    nicho = models.CharField(max_length=150, blank=True)

    conteudo = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.tema} ({self.created_at:%d/%m/%Y})"
