from django.db import migrations

def seed_plans(apps, schema_editor):
    Plan = apps.get_model('billing', 'Plan')

    plans = [
        {
            'name': 'Basic',
            'price': 29.00,
            'external_reference': 'basic_monthly',
            'max_posts': 100,
            'has_ai': True,
            'active': True,
            'recurrence': 'monthly',
        },
        {
            'name': 'Creator',
            'price': 69.00,
            'external_reference': 'creator_monthly',
            'max_posts': 500,
            'has_ai': True,
            'active': True,
            'recurrence': 'monthly',
        },
        {
            'name': 'Elite',
            'price': 149.00,
            'external_reference': 'elite_monthly',
            'max_posts': 2000,
            'has_ai': True,
            'active': True,
            'recurrence': 'monthly',
        },
    ]

    for p in plans:
        Plan.objects.get_or_create(
            external_reference=p['external_reference'],
            defaults=p
        )

class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0001_initial'),  # ajuste se necessário
    ]

    operations = [
        migrations.RunPython(seed_plans),
    ]
