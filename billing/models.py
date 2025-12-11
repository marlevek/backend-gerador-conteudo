from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta


class Plan(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    external_reference = models.CharField(max_length=150)
    recurrence = models.CharField(max_length=20, choices=(
        ('monthly', 'Mensal'),
        ('yearly', 'Anual'),
    ))

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    last_payment_status = models.CharField(max_length=50, default="pending")

    def activate(self):
        self.active = True
        self.end_date = datetime.now() + timedelta(days=30)
        self.last_payment_status = "paid"
        self.save()

    def deactivate(self, status):
        self.active = False
        self.last_payment_status = status
        self.save()

    def __str__(self):
        return f"{self.user} - {self.plan} - Ativa: {self.active}"
