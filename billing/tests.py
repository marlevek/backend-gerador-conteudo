from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from rest_framework.test import APITestCase
from rest_framework.response import Response
from billing.models import Plan, Subscription
from billing.utils import get_valid_subscription
from billing.utils import get_or_create_monthly_usage
from api.decorators import assinatura_ativa_required
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from rest_framework.test import APIClient




class GetValidSubscriptionTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test@test.com",
            email="test@test.com",
            password="123456"
        )

        self.plan = Plan.objects.create(
            name="Basic",
            price=0,
            external_reference="basic_test",
            max_posts=10
        )

    def test_trial_valido(self):
        Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status="trial",
            end_date=now() + timedelta(days=3)
        )

        sub = get_valid_subscription(self.user)
        self.assertIsNotNone(sub)

    def test_trial_vencido(self):
        Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status="trial",
            end_date=now() - timedelta(days=1)
        )

        sub = get_valid_subscription(self.user)
        self.assertIsNone(sub)

    def test_assinatura_ativa(self):
        Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status="active",
            active=True,
            end_date=now() + timedelta(days=30)
        )

        sub = get_valid_subscription(self.user)
        self.assertIsNotNone(sub)

    def test_sem_assinatura(self):
        sub = get_valid_subscription(self.user)
        self.assertIsNone(sub)



class UsageMeViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="user@test.com",
            email="user@test.com",
            password="123456"
        )

        self.plan = Plan.objects.create(
            name="Basic",
            price=0,
            external_reference="basic_test",
            max_posts=10
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_acesso_com_trial_valido(self):
        Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status="trial",
            end_date=now() + timedelta(days=5)
        )

        response = self.client.get(reverse("usage_me"))

        self.assertEqual(response.status_code, 200)

    def test_bloqueio_trial_vencido(self):
        Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status="trial",
            end_date=now() - timedelta(days=1)
        )

        response = self.client.get(reverse("usage_me"))
        self.assertEqual(response.status_code, 403)
        
        
class DecoratorTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="decor@test.com",
            email="decor@test.com",
            password="123456"
        )

        self.plan = Plan.objects.create(
            name="Basic",
            price=0,
            external_reference="basic_test",
            max_posts=10
        )

        self.client.login(username="decor@test.com", password="123456")

        def test_decorator_bloqueia_sem_assinatura(self):
            factory = APIRequestFactory()
            request = factory.get("/fake-url/")
            request.user = AnonymousUser()

            @assinatura_ativa_required
            def fake_view(self, request):
                return Response({"ok": True})

            response = fake_view(self, request)
            self.assertEqual(response.status_code, 403)