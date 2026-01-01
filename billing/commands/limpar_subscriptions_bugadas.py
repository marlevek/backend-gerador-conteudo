from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.contrib.auth import get_user_model

from billing.models import Subscription, Plan
from billing.utils import get_valid_subscription

User = get_user_model()


class Command(BaseCommand):
    help = "Remove subscriptions bugadas (Creator/Elite sem pagamento e trials inválidos)"

    def handle(self, *args, **options):
        basic_plan = Plan.objects.get(name="Basic")

        usuarios_corrigidos = 0
        subs_removidas = 0

        for user in User.objects.all():
            subs = Subscription.objects.filter(user=user).order_by("-start_date")

            if not subs.exists():
                continue

            valid_sub = get_valid_subscription(user)

            # CASO 1 — tem assinatura válida paga
            if valid_sub:
                for sub in subs:
                    if sub.id != valid_sub.id:
                        sub.delete()
                        subs_removidas += 1
                continue

            # CASO 2 — não tem assinatura válida
            trial_basic = subs.filter(status="trial", plan=basic_plan).first()

            for sub in subs:
                if trial_basic and sub.id == trial_basic.id:
                    continue
                sub.delete()
                subs_removidas += 1

            if not trial_basic:
                Subscription.objects.create(
                    user=user,
                    plan=basic_plan,
                    status="trial",
                    active=False,
                    start_date=now(),
                    end_date=now(),
                )

            usuarios_corrigidos += 1

        self.stdout.write(self.style.SUCCESS("✅ LIMPEZA CONCLUÍDA"))
        self.stdout.write(f"Usuários corrigidos: {usuarios_corrigidos}")
        self.stdout.write(f"Subscriptions removidas: {subs_removidas}")
